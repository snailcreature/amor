from argparse import ArgumentParser, Namespace
from git.refs.head import HEAD
from toml import load, dump
from os import mkdir, path, getcwd, environ, listdir, rename
from shutil import ignore_patterns, rmtree, copytree
from subprocess import PIPE, run as cmd
from luaparser import ast
from git import Repo
from lupa.lua54 import LuaRuntime


lua = LuaRuntime()

default_conf = {
            "project": {
                "name": "",
                "version": "0.0.1",
                "author": "",
                "description": "",
                "license": "",
                "love_version": "",
                "lua_version": "5.4",
                "source_dir": "src",
                "build_dir": "build",
                "entry": "main.lua",
                },
            "scripts": {
                "test": "echo \"Hello, World!\"",
                "build": "echo \"No build script defined!\"",
                },
            "dependencies": {},
            "dev_dependencies": {},
            }

gitignore_lines = [
        "/build\n",
        "/dist\n",
        "/.amor\n"
        ]


def getRepoTags(repo_url: str):
    res = cmd(["git", "ls-remote", "--tags", repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    tags = [
            line.split("refs/tags/")[-1] for line in out_lines
            if "refs/tags/" in line and "^{}" not in line
        ]
    return tags


def getRepoTagHashes(repo_url: str):
    res = cmd(["git", "ls-remote", "--tags", repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    tagHashes: dict[str, str] = {}
    
    for line in out_lines:
        if "refs/tags/" not in line or "^{}" in line:
            continue
        
        hash, tag = line.split('refs/tags/')
        tagHashes[tag] = hash.replace('\t', '')

    return tagHashes

def getRepoHeads(repo_url: str):
    res = cmd(['git', 'ls-remote', '--heads', repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    for line in out_lines: print(line)

    heads = [
            line.split('refs/heads/')[0].replace('\t', '') for line in out_lines
            if "refs/heads/" in line and "^{}" not in line
            ]

    return heads


def getRepoHeadHash(repo_url: str):
    res = cmd(['git', 'ls-remote', repo_url, 'HEAD'], shell=False, stdout=PIPE,
            text=True)
     
    out_lines = res.stdout.splitlines()

    res.check_returncode()

    head = out_lines[0].split('HEAD')[0].replace('\t', '')

    return head


def newOpt(args: Namespace):
    name = args.name[0]
     
    if name == '.':
        print("Please run `amor init` to start your project in the current\
                directory.")
        return

    conf = default_conf

    conf["project"]["name"] = name
    
    print("Making directory ./"+name+"...")
    mkdir('./'+name)
    mkdir('./'+name+'/src')

    print("Creating ./"+name+"/amor.conf...")
    with open('./'+name+'/amor.toml', 'w') as conf_file:
        dump(conf, conf_file)

    if args.git_init:
        print("Creating .gitignore...")
        with open("./"+name+"/.gitignore", 'w') as gitignore:
            gitignore.writelines(gitignore_lines)

        print("Initialising git repo...")
        repo = Repo.init(path.join(name))
        repo.index.add([".gitignore",
            "amor.toml"
            ])
        repo.index.commit("Initial commit")
    
    print("New project", name, "created!")
    return


def initOpt(args: Namespace):
    with open('amor.toml', 'r') as conf:
        amor_conf: dict = load(conf)

    if not args.force and len(amor_conf.keys()) != 0:
        print('amor.toml already exists!\nRun with --force to reset the config\
              file')
        return

    amor_conf = default_conf
    
    print("Creating amor.toml...")
    if args.project_name != None:
        amor_conf["project"]["name"] = args.project_name

    with open('amor.toml', 'w') as conf:
        dump(amor_conf, conf)

    if args.git_init:
        print("Creating .gitignore...")
        with open(".gitignore", 'w') as gitignore:
            gitignore.writelines(gitignore_lines)

        print("Initialising git repo...")
        repo = Repo.init('.')
        repo.index.add([
            ".gitignore",
            "amor.toml"
            ])

    print("Project initialised!")

    return


def installOpt(args: Namespace):
    modules: list[str] = args.module
    
    hashes = {}

    if args.force:
        for dir in listdir('./.amor'):
            try:
                rmtree(f"./.amor/{dir}/")
            except:
                print(f'Failed to delete {dir}')

    if len(modules) == 0:
        print('Installing from amor.toml...')
        with open('amor.toml', 'r') as amor_conf:
            conf = load(amor_conf)

        found_mods: dict[str, str] = conf["dependencies"]
        for mod in found_mods.keys():
            if path.exists(f"./.amor/{mod}"):
                print(f"{mod} already installed!")
                continue
            
            mod_name, mod_hash = conf["dependencies"][mod].split('=')
            modules.append(mod_name)
            mod_name = mod_name.split('@')[0]
            hashes[mod_name] = mod_hash
            print(mod_name, mod_hash)


    for module in modules:
        print('Installing', module+"...")
        if path.exists('./.amor/tmp/'):
            rmtree('./.amor/tmp/')

        tag = None
        repo = module
        if '@' in module:
            repo, tag = module.split('@')
        module_name = repo.split('/')[-1]
    
        if tag == 'None':
            tag = None

        git_url = f"https://github.com/{repo}.git"
        tags = getRepoTagHashes(git_url)

        hash = ''
        if tag != None and tag in tags.keys():
            hash = tags[tag]
        else:
            hash = getRepoHeadHash(git_url)
        print(tag, hash)
        
        if len(hashes.keys()) > 0:
            try:
                r = Repo.clone_from(git_url, to_path='./.amor/tmp/')
                r.index.reset(commit=hashes[repo], working_tree=True)
            except KeyError:
                print('Something went wrong resetting the HEAD!')
        else:
            Repo.clone_from(git_url, to_path="./.amor/tmp/", branch=tag,
                        depth=1)
        
        dir_content = listdir('./.amor/tmp')
        rockspecs = [file for file in dir_content if file.endswith('.rockspec')]
        makefiles = [file for file in dir_content if "Makefile" in file]

        if len(rockspecs) > 0:
            print('Building from Rockspec...')
            res = cmd(["luarocks", "build", rockspecs[0], f'--tree="build"',], cwd="./.amor/tmp/",
                      stdout=PIPE, text=True)

            for line in res.stdout.splitlines(): print(line)

            res.check_returncode()
            
            with open(f"./.amor/tmp/{rockspecs[0]}", 'r') as rs:
                rspec = rs.readlines()

            rspec.append(
                    "if build and build.modules then return build.modules end\n"
                    )                                                                          
            build_modules = lua.execute(''.join(rspec))

            mods = [mod for mod in build_modules.keys()]

            if len(mods) > 0:
                module_name = mods[0]

            if path.exists(f"./.amor/{module_name}"):
                rmtree(f"./.amor/{module_name}")

            cwd = getcwd()
            copytree(f"{cwd}/.amor/tmp/build/lib/lua/5.4/", f"{cwd}/.amor/{module_name}/")

        elif len(makefiles) > 0:
            print('Building from Makefile...')
            for makefile in makefiles:
                with open(f"./.amor/tmp/{makefile}", "r") as mf:
                    lines = mf.readlines()

                for i in range(len(lines)):
                    if 'config' in lines[i] or 'CONFIG' in lines[i]:
                        lines[i] = f"# {lines[i]}"

                with open(f"./.amor/tmp/{makefile}", "w") as mf:
                    mf.writelines(lines)

            LUA_INCLUDE = environ.copy()["LUA_INCLUDE"]
            print(LUA_INCLUDE)
            res = cmd(["make", f"--include-dir={LUA_INCLUDE}"], stdout=PIPE,
                      shell=True, text=True, cwd='./.amor/tmp/')

        else:
            print('No build option found! Copying files...')

            if path.exists(f"./.amor/{module_name}"):
                rmtree(f"./.amor/{module_name}")

            copytree("./.amor/tmp", f"./.amor/{module_name}",
                     ignore=ignore_patterns("*.git*", "*.md"))
        
        rmtree('./.amor/tmp')

        with open('amor.toml', 'r') as amor_conf:
            conf = load(amor_conf)

        if conf['dependencies'] is None:
            conf['dependencies'] = {}

        conf['dependencies'][module_name] = f"{repo}@{tag}={hash}"

        with open('amor.toml', 'w') as amor_conf:
            dump(conf, amor_conf)

        print(f"Installed {module_name}!")
    return


def runOpt(args: Namespace):
    script = args.script[0]
    with open('amor.toml', 'r') as conf:
        amor_conf: dict = load(conf)

    scripts: dict = amor_conf["scripts"]

    if script not in scripts.keys():
        print(script, "not defined!")
        return

    parts: list[str] = scripts[script].split(' && ')
    print('Running script', scripts[script])
    for part in parts:
        print('>', part)
        res = cmd(part.split(" "), stdout=PIPE, text=True)

        for line in res.stdout.splitlines(): print(line)

        res.check_returncode()
    return


def buildOpt(args: Namespace):
    with open('amor.toml', 'r') as conf_file:
        conf = load(conf_file)

    source_dir = conf["project"]["source_dir"]
    entry = conf["project"]["entry"]

    with open('./'+source_dir+'/'+entry, 'r') as lua_file:
        lua_code = ''.join(lua_file.readlines())

    lua_ast = ast.parse(lua_code)

    ast.to_pretty_str(lua_ast)

    print(ast.to_lua_source(lua_ast))

    path = lua.eval('package.path')
    print("\nPath:", path)

    cpath = lua.eval('package.cpath')
    print("\nCPath:", cpath)

    print("\nCWD:", getcwd())

    return


def loveOpt(_args: Namespace):
    with open('amor.toml', 'r') as conf:
        amor_conf = load(conf)

    build_dir = amor_conf["project"]["build_dir"]
    cwd = getcwd()
    lua_env = environ.copy()
    lua_env["LUA_PATH"] = f"{cwd}/.amor/?/init.lua;{cwd}/.amor/?.lua;\
            {lua_env['LUA_PATH']}"
    lua_env["LUA_CPATH"] = f"{cwd}/.amor/?.so;{cwd}/.amor/?/?.so;{lua_env['LUA_CPATH']}"
        
    res = cmd(["love", build_dir], stdout=PIPE, text=True, env=lua_env)

    for line in res.stdout.splitlines(): print(line)
    
    res.check_returncode()
    return
    

parser = ArgumentParser(description="A package manager for the Löve game engine.")

subparsers = parser.add_subparsers(help="Additional commands")

# New
newParse = subparsers.add_parser("new", help="Create a new project folder.")
newParse.add_argument("name", nargs=1, type=str, help="The name of the\
        project. A directory with this name will be created.")
newParse.add_argument("--git-init", "-g", action="store_true", help="Initialise\
        git repository in project.")
newParse.set_defaults(func=newOpt)

# Init
init = subparsers.add_parser("init", help="Initialise an Amor project.")
init.add_argument("project_name", nargs="?", type=str, help="The name of the\
                  project.")
init.add_argument("--force", '-f', action="store_true", help="Force the\
                  creation of a fresh amor.toml config file.")
init.add_argument("--git-init", '-g', action="store_true", help="Initialise\
        git repository in project.")
init.set_defaults(func=initOpt)

# Install
install = subparsers.add_parser("install", aliases=["i", "add"], help="Install\
        the given module to this project.")
install.add_argument('--force', '-f', action="store_true", help="Force the\
        force the re-installation of all modules.")
install.add_argument("module", nargs="*", type=str, help="Modules to install\
                     from Github. Given in format\
                     `<username>/<repository>[@<tag>]`. If <tag> is not present\
                     the most current version will be installed. If <tag> is\
                     present, but does not exist on repository, the most\
                     current version will be installed.")
install.set_defaults(func=installOpt)

# Uninstall

# Run
run = subparsers.add_parser("run", aliases=["r"], help="Run a script defined in\
        the project amor.toml config file.")
run.add_argument("script", nargs=1, type=str, help="Name of script to run.")
run.set_defaults(func=runOpt)

# Build
build = subparsers.add_parser("build", aliases=["b"], help="Build project into\
        single directory for Löve.")
build.set_defaults(func=buildOpt)

# Love
love = subparsers.add_parser("love", help="Run Löve using the current project's\
        build directory.")
love.set_defaults(func=loveOpt)

args = parser.parse_args()
args.func(args)

