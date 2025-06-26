from argparse import Namespace

def buildOpt(args: Namespace):
    """
    Build the project.
    """
    from toml import load
    from os import path, mkdir, listdir
    from luaparser import ast, astnodes
    from pickle import load as pload, dump as pdump
    from shutil import rmtree, copytree, copyfile
    from fnmatch import fnmatch
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

    from constants import init_lua_template

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
    
    if args.clean:
        rmtree(f'./{build_dir}')

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
            print(p)
            if path.isdir(f"{dir}/{p}"):
                asset_dict[p] = recRegisterAssets(f"{dir}/{p}", {})
            else:
                print(f"Checking {dir}/{p} against", *include)
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
    print(*assets)
    if len(assets.keys()) > 0:
        print("Found assets")
        print(assets)
        recCopyAssets("", assets)
    else:
        print("No assets found")
    return


