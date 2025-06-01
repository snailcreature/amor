from argparse import ArgumentParser, Namespace
from typing import Any
from toml import load, dump
from os import mkdir, path, getcwd, environ, listdir
from shutil import copyfile, rmtree, copytree
from subprocess import PIPE, run as cmd
from luaparser import ast, astnodes
from git import Repo
from pickle import load as pload, dump as pdump
from fnmatch import filter as fil, fnmatch
try:
    from lupa.lua54 import LuaRuntime
except ImportError:
    try:
        from lupa.lua53 import LuaRuntime
    except ImportError:
        try:
            from lupa.lua52 import LuaRuntime
        except ImportError:
            from lupa.lua51 import LuaRuntime



# Default configuration
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
            "build": {
                "include": [
                    "*.png",
                    ],
                },
            "scripts": {
                "test": "echo \"Hello, World!\"",
                "build": "echo \"No build script defined!\"",
                },
            "dependencies": {},
            }

# Default .gitignore for projects
gitignore_lines = """\
/build
/dist
/.amor
""".splitlines(keepends=True)

# Default .gitattributes for projects
gitattributes_lines = """\
# Normalise line endings
* text=auto

# Enforce Unix line endings
* text eol=lf

# Treat these as binaries
*.png binary

""".splitlines(keepends=True)

# Basic Love2D entry file
main_lua_content = """\
function love.load(arg)
end

function love.update(dt)
end

function love.draw()
end
""".splitlines(keepends=True)

# Template for init.lua for C modules
init_lua_template = """\
local Path = (...):gsub("%p", "/")
local RequirePath = ...
local {mod} = package.loadlib("{mod}", Path.."/{mod}.so")
package.loaded["{mod}"] = {mod}
return {mod}
"""


def getRepoTags(repo_url: str):
    """
    Get the tags of a remote repository.
    """
    res = cmd(["git", "ls-remote", "--tags", repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    tags = [
            line.split("refs/tags/")[-1] for line in out_lines
            if "refs/tags/" in line and "^{}" not in line
        ]
    return tags


def getRepoTagHashes(repo_url: str):
    """
    Get the hashes for the tagged releases of a remote repository.
    """
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
    """
    Get the HEAD commits of a remote repository.
    """
    res = cmd(['git', 'ls-remote', '--heads', repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    for line in out_lines: print(line)

    heads = [
            line.split('refs/heads/')[0].replace('\t', '') for line in out_lines
            if "refs/heads/" in line and "^{}" not in line
            ]

    return heads


def getRepoHeadHash(repo_url: str):
    """
    Get the hash for the HEAD commit of a remote repository.
    """
    res = cmd(['git', 'ls-remote', repo_url, 'HEAD'], shell=False, stdout=PIPE,
            text=True)
     
    out_lines = res.stdout.splitlines()

    res.check_returncode()

    head = out_lines[0].split('HEAD')[0].replace('\t', '')

    return head


def newOpt(args: Namespace):
    """
    Create a new repository from scratch.
    """
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
    with open('./'+name+'/src/main.lua') as main_lua:
        main_lua.writelines(main_lua_content)

    print("Creating ./"+name+"/amor.conf...")
    with open('./'+name+'/amor.toml', 'w') as conf_file:
        dump(conf, conf_file)

    if args.git_init:
        print("Creating .gitignore...")
        with open("./"+name+"/.gitignore", 'w') as gitignore:
            gitignore.writelines(gitignore_lines)

        with open("./"+name+"/.gitattributes", 'w') as gitattributes:
            gitattributes.writelines(gitattributes_lines)

        print("Initialising git repo...")
        repo = Repo.init(path.join(name))
        repo.index.add([".gitignore",
                ".gitattributes",
                "amor.toml"
            ])
        repo.index.commit("Initial commit")
    
    print("New project", name, "created!")
    return


def initOpt(args: Namespace):
    """
    Initialise amor in the current repository.
    """
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

        with open(".gitattributes", "w") as gitattributes:
            gitattributes.writelines(gitattributes_lines)

        print("Initialising git repo...")
        repo = Repo.init('.')
        repo.index.add([
            ".gitattributes",
            ".gitignore",
            "amor.toml"
            ])

    print("Project initialised!")

    return


def include_patterns(*patterns):
    """
    Define the patterns to include in the tree when using shutil.copytree().
    """
    def _ignore_patterns(p: Any, names: list[str]):
        keep = set(name for pattern in patterns
                   for name in fil(names, pattern))

        ignore = set(name for name in names
                     if name not in keep and not path.isdir(path.join(p,
                                                                      name)))
        return ignore
    return _ignore_patterns


def installOpt(args: Namespace):
    """
    Install given repositor(y/ies) or all repositories in the project amor.toml.
    """
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
            lua = LuaRuntime()
            build_modules = lua.execute(''.join(rspec))

            mods = [mod for mod in build_modules.keys()] # type: ignore

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
            
            for line in res.stdout.splitlines(): print(line)

            res.check_returncode()

        else:
            print('No build option found! Copying files...')

            if path.exists(f"./.amor/{module_name}"):
                rmtree(f"./.amor/{module_name}")

            copytree("./.amor/tmp", f"./.amor/{module_name}",
                     ignore=include_patterns("*.lua", "*.so"))
        
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


def uninstallOpt(args: Namespace):
    """
    Uninstall the given repositor(y/ies).
    """
    modules: list[str] = args.module

    with open('amor.toml', 'r') as amor_conf:
        conf = load(amor_conf)

    deps: dict[str, str] = conf["dependencies"]

    to_delete: list[str] = [dep for dep in deps if dep in modules]

    for dep in to_delete:
        print(f'Uninstalling {dep}')
        try:
            rmtree(f'./.amor/{dep}')

            del conf["dependencies"][dep]
        except:
            print(f'Failed to uninstall {dep}.') 
    
    with open('amor.toml', 'w') as amor_conf:
        dump(conf, amor_conf)

    return


def runOpt(args: Namespace):
    """
    Run a given script name from the project amor.toml.
    """
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
    """
    Build the project.
    """
    with open('amor.toml', 'r') as conf_file:
        conf = load(conf_file)

    source_dir = conf["project"]["source_dir"]
    build_dir = conf["project"]["build_dir"]
    entry = conf["project"]["entry"]
    include = conf["build"]["include"]

    lua = LuaRuntime()

    lpath = lua.eval('package.path')
    cpath = lua.eval('package.cpath')
    lua_path = f'./.amor/?.lua;./{source_dir}/?.lua;./.amor/?/init.lua;{str(lpath)};'
    lua_cpath = f';./.amor/?.so;./.amor/?/?.so;./{source_dir}/?.so;{str(cpath)};'
    
    if not path.exists('./.bld'):
        mkdir('./.bld')


    def recScanSource(file_path: str, mod_map: dict[str, str]) -> dict[str, str]:
        """
        Scan the project source for required modules.
        """
        with open(file_path, 'r') as src_file:
            lua_code = ''.join(src_file.readlines())

        lua_ast = ast.parse(lua_code)

        for node in ast.walk(lua_ast): # type: ignore
            if isinstance(node, astnodes.Call):
                node: astnodes.Call = node
                if isinstance(node.func, astnodes.Name):
                    func: astnodes.Name = node.func # type: ignore

                    if func.id == 'require':
                        mod: astnodes.String = node.args[0] # type: ignore

                        res = lua.eval(f'package.searchpath("{mod.s}",\
                                "{lua_path+lua_cpath}")')
                        if '(None,' in str(res):
                             print(f'Could not find {mod.s}')
                             continue

                        mod_map[mod.s] = str(res)
        
        
        split_path = file_path.split('/')
        bld_path = '/'.join(["./.bld"] + split_path[2:]).replace('.lua', '.dat')
        if len(split_path) > 2 and not split_path[1].endswith('.lua'):
            for i in range(2, len(split_path)-1):
                tmp = '/'.join(split_path[2:i+1])
                if not path.exists(f"./.bld/{tmp}"):
                    mkdir(f"./.bld/{tmp}")
       
        with open(bld_path, 'wb') as dat:
            pdump(lua_ast, dat)

        print('Scanned', file_path)
        for p in mod_map.copy().values():
            if f"./{source_dir}/" in p:
                print(p)
                sub_mod_map = recScanSource(p, {})
                for v in sub_mod_map.keys(): mod_map[v] = sub_mod_map[v]

        return mod_map

    mod_map: dict[str, str] = recScanSource(f'./{source_dir}/{entry}', {})
                
    for key in mod_map.keys(): print(key, mod_map[key])

    if not path.exists(f"./{build_dir}"):
        mkdir(f"./{build_dir}")

    if not path.exists(f"./{build_dir}/ext"):
        mkdir(f"./{build_dir}/ext")

    for key in mod_map.keys():
        if not f"./{source_dir}/" in mod_map[key]:
            copy_path = mod_map[key].split('/')[:-1]
            mod_dir = copy_path[-1]
            out_dir = f"./{build_dir}/ext/{mod_dir}"
            if path.exists(out_dir):
                rmtree(out_dir)
            copytree('/'.join(copy_path), f"./{build_dir}/ext/{mod_dir}")
            print("Copied", mod_map[key])
            if mod_map[key].endswith('.so'):
                init_lua_content = init_lua_template.replace("{mod}", key)
                with open(f"./{build_dir}/ext/{mod_dir}/init.lua", "w") as init_file:
                    init_file.writelines(init_lua_content.splitlines(keepends=True))

    
    def recCompile(directory: str):
        """
        Compile the project source directory.
        """
        dir_list = listdir(directory)

        for dir in dir_list:
            full_path = directory+'/'+dir
            if path.isdir(full_path):
                recCompile(full_path)
            else:
                with open(full_path, 'rb') as dat:
                    tree = pload(dat)
                
                comped = ast.to_lua_source(tree)

                for mod in mod_map.keys():
                    if not f"./{source_dir}/" in mod_map[mod]:
                        comped = comped.replace(f"require(\"{mod}", f"require(\"ext.{mod}")
                        comped = comped.replace(f"require('{mod}",
                                                          f"require('ext.{mod}")

                out_dir = full_path.split('/')
                comp_path = '/'.join([f'./{build_dir}'] +
                                     out_dir[2:]).replace('.dat', '.lua')
                if len(out_dir) > 2 and not out_dir[1].endswith('.dat'):
                    for i in range(2, len(out_dir)-1):
                        tmp = '/'.join(out_dir[2:i+1])
                        if not path.exists(f'./{build_dir}/{tmp}'):
                            mkdir(f"./{build_dir}/{tmp}")

                with open(comp_path, 'w') as out:
                    out.write(comped)
                print('Built', comp_path)
        return


    recCompile('./.bld')

    def recRegisterAssets(dir: str, asset_dict = {}):
        """
        Register assets in the project source based on the build.include pattern
        list.
        """
        print(f'Checking {dir}...')
        directory = listdir(dir)
        
        for p in directory:
            if path.isdir(f"{dir}/{p}"):
                asset_dict[p] = recRegisterAssets(f"{dir}/{p}", {})
            else:
                for pattern in include:
                    if fnmatch(p, pattern):
                        print(f"Found {dir}/{p}")
                        asset_dict[p] = True
                        break

        for key in asset_dict.copy().keys():
            if type(asset_dict[key]) is dict and len(asset_dict[key].keys()) == 0:
                del asset_dict[key]

        return asset_dict
    

    def recCopyAssets(dir: str, asset_dict: dict):
        """
        Recursively copy assets based on the output of recRegisterAssets.
        """
        if not path.exists(f"./{build_dir}/{dir}"):
            mkdir(f"./{build_dir}/{dir}")
        
        for key in asset_dict.keys():
            if type(asset_dict[key]) == dict:
                recCopyAssets(f"{dir}/{key}", asset_dict[key])
            else:
                print(f"Copying ./{source_dir}/{dir}/{key}...")
                copyfile(f"./{source_dir}/{dir}/{key}",
                         f"./{build_dir}/{dir}/{key}")
        return


    print(include)
    assets = recRegisterAssets(f"./{source_dir}")
    if len(assets.keys()) > 0:
        print("Found assets")
        print(assets)
        recCopyAssets("", assets)
    else:
        print("No assets found")
    return


def loveOpt(_args: Namespace):
    """
    Run Löve2D on the project build directory.
    """
    with open('amor.toml', 'r') as conf:
        amor_conf = load(conf)

    build_dir = amor_conf["project"]["build_dir"]
    cwd = getcwd()
    lua_env = environ.copy()
    lua_env["LUA_PATH"] = f"?;?.lua;{cwd}/{build_dir}/?/init.lua;{cwd}/{build_dir}/?.lua;\
            {lua_env['LUA_PATH']}"
    lua_env["LUA_CPATH"] = f"?;?.so;{cwd}/{build_dir}/?.so;{cwd}/{build_dir}/?/?.so;{lua_env['LUA_CPATH']}"
        
    res = cmd(["love", build_dir], stdout=PIPE, text=True, env=lua_env)

    for line in res.stdout.splitlines(): print(line)
    
    res.check_returncode()
    return
    


# Parser
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
        the given module(s) to this project.")
install.add_argument('--force', '-f', action="store_true", help="Force the\
        force the re-installation of all modules.")
install.add_argument("module", nargs="*", type=str, help="Module(s) to install\
                     from Github. Given in format\
                     `<username>/<repository>[@<tag>]`. If <tag> is not present\
                     the most current version will be installed. If <tag> is\
                     present, but does not exist on repository, the most\
                     current version will be installed.")
install.set_defaults(func=installOpt)

# Uninstall
uninstall = subparsers.add_parser('uninstall', aliases=['u', 'remove'], help="\
        Uninstall the given module(s) from the project.")
uninstall.add_argument('module', nargs="+", type=str, help="Module(s) to\
        uninstall, given in format `<module_name>` (as you would require\
        in a Lua script).")
uninstall.set_defaults(func=uninstallOpt)

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

