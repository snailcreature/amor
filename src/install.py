from argparse import Namespace

def installOpt(args: Namespace):
    """
    Install given repositor(y/ies) or all repositories in the project amor.toml.
    """
    from os import listdir, path, getcwd, environ
    from shutil import rmtree, copytree
    from toml import load, dump
    from git import Repo
    from subprocess import PIPE, run as cmd
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


    from utils import getRepoHeadHash, getRepoTagHashes, include_patterns, remove_empty_dirs

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
        mod_name = repo.split('/')[-1]
    
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
        
        built_from_spec = False
        built_from_rockspec = False
        built_from_makefile = False
        try:
            if len(rockspecs) > 0:
                print('Building from Rockspec...')
                res = cmd(["luarocks", "build", rockspecs[0], f'--tree="build"',], cwd="./.amor/tmp/",
                      stdout=PIPE, text=True)

                for line in res.stdout.splitlines(): print(line)

                res.check_returncode()
            
                with open(f"./.amor/tmp/{rockspecs[0]}", 'r') as rs:
                    rspec = rs.readlines()

                rspec.append(
                        "if build and package then return { package = package,\
                                                           modules = build.modules} end\n"
                        )
                lua = LuaRuntime()
                build_modules = dict(lua.execute(''.join(rspec))) # type: ignore
                print(build_modules)
                mods: list[str] = [mod for mod in build_modules["modules"]] # type: ignore
                package: str | None = build_modules['package'] # type: ignore

                print(*mods)
                print(build_modules["package"]) # type: ignore
                has_package = package is not None
                renamed_mod = list(filter(lambda m: '.' not in m, mods))
                mismatch_module_name = len(renamed_mod) != 0 and package not in renamed_mod
                print(*renamed_mod)

                if has_package:
                    print('has package', package)
                    mod_name = package
                if mismatch_module_name:
                    print('but has mismatch', renamed_mod[0])
                    mod_name = renamed_mod[0]
                if not has_package and not mismatch_module_name and len(mods) > 0:
                    print('fallback')
                    mod_name = mods[0]

                if path.exists(f"./.amor/{mod_name}"):
                    rmtree(f"./.amor/{mod_name}")

                cwd = getcwd()
                try:
                    copytree(f"{cwd}/.amor/tmp/build/lib/lua/5.4/", f"{cwd}/.amor/{mod_name}/")
                except:
                    print("Default build location not found, trying fallback...")
                    try:
                        copytree(f"{cwd}/.amor/tmp/build/share/lua/5.4/{mod_name}/",
                             f"{cwd}/.amor/{mod_name}/")
                    except:
                        print(f"Uh oh! {mod_name} could not be built!")
                        raise
                built_from_rockspec = True

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
                built_from_makefile = True
        except:
            print('Something went wrong whilst building, attempting source \
                  copy...')
        else:
            print('No errors!')
            built_from_spec = built_from_rockspec or built_from_makefile
        finally:
            print('Final checks...')
            if not built_from_spec:
                print('No build option found! Copying files...')

                if path.exists(f"./.amor/{mod_name}"):
                    rmtree(f"./.amor/{mod_name}")

                copytree("./.amor/tmp", f"./.amor/{mod_name}",
                        ignore=include_patterns("*.lua", "*.so"))

                remove_empty_dirs(f"./.amor/{mod_name}/")
        
        rmtree('./.amor/tmp')

        with open('amor.toml', 'r') as amor_conf:
            conf = load(amor_conf)

        if conf['dependencies'] is None:
            conf['dependencies'] = {}

        conf['dependencies'][mod_name] = f"{repo}@{tag}={hash}"

        with open('amor.toml', 'w') as amor_conf:
            dump(conf, amor_conf)

        print(f"Installed {mod_name}!")
    return


