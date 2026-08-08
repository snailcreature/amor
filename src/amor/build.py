from typing import Annotated
import typing

import typer

app = typer.Typer()


@app.command("b", hidden=True)
@app.command()
def build(
    clean: Annotated[
        bool,
        typer.Option("--clean/", "-c/", help="Remove existing build folder contents."),
    ] = False,
):
    """
    Build project into single directory for Löve.
    (Aliases: `b`)
    """
    from toml import load
    from os import path, mkdir, listdir, getcwd
    from luaparser import ast, astnodes
    from pickle import load as pload, dump as pdump
    from shutil import rmtree, copytree, copyfile
    from fnmatch import fnmatch
    from re import sub
    from rich import print

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

    from .constants import init_lua_template_so, init_lua_template_lua, love_builtins

    # Get configs
    with open("amor.toml", "r") as conf_file:
        conf = load(conf_file)

    source_dir = conf["project"]["source_dir"]
    build_dir = conf["project"]["build_dir"]
    entry = conf["project"]["entry"]
    include = conf["build"]["include"]

    lua = LuaRuntime(unpack_returned_tuples=False)

    cwd = getcwd()
    lpath = lua.eval("package.path")
    cpath = lua.eval("package.cpath")
    lua_path = f"./.amor/?.lua;./.amor/?/init.lua;./.amor/?/?.lua;./{source_dir}/?.lua;\
            ./{source_dir}/?/init.lua;./{source_dir}/?/?.lua;{lpath}"
    lua_cpath = f"{cwd}/.amor/?.so;./.amor/?/?.so;./{source_dir}/?.so;{cpath}"

    print(lua.eval("os.getenv('PWD')"))
    # print(lua_path)
    if clean:
        rmtree(f"./{build_dir}")

    if not path.exists("./.bld"):
        mkdir("./.bld")

    def recScanSource(file_path: str, mod_map: dict[str, str]) -> dict[str, str]:
        """
        Scan the project source for required modules.
        """
        with open(file_path, "r") as src_file:
            lua_code = "".join(src_file.readlines())

        # Parse the code into an AST
        lua_ast: ast.Chunk = ast.parse(lua_code)

        node: ast.Node | None
        for node in ast.walk(lua_ast):
            # Function call
            if isinstance(node, astnodes.Call):
                call_node: astnodes.Call = typing.cast(astnodes.Call, node)
                # Function has name
                if isinstance(call_node.func, astnodes.Name):
                    func: astnodes.Name = typing.cast(astnodes.Name, call_node.func)

                    # It's a require function
                    if func.id == "require":
                        # Module name will be first arg in the function
                        mod: astnodes.String = call_node.args[0]
                        if mod.raw in love_builtins:
                            print(f"{mod.raw} included with Love")
                            continue
                        # Search the path for this module
                        res: (str, None) | (None, str) = lua.eval(
                            f'package.searchpath("{mod.raw}",\
                                "{lua_path + lua_cpath}")'
                        )

                        print(res[0], "\n", res[1])
                        if res[0] is None:
                            if mod.raw in love_builtins:
                                print(f"{mod.raw} included with Love")
                            else:
                                print(f"Could not find {mod.raw}")
                            continue

                        mod_map[mod.raw] = res

        # Save the found modules to .dat file
        split_path = file_path.split("/")
        bld_path = "/".join(["./.bld"] + split_path[2:]).replace(".lua", ".dat")
        if len(split_path) > 2 and not split_path[1].endswith(".lua"):
            for i in range(2, len(split_path) - 1):
                tmp = "/".join(split_path[2 : i + 1])
                # Save the dat file to the bld folder
                if not path.exists(f"./.bld/{tmp}"):
                    mkdir(f"./.bld/{tmp}")

        with open(bld_path, "wb") as dat:
            pdump(lua_ast, dat)

        print("Scanned", file_path)
        for p in mod_map.copy().values():
            if f"./{source_dir}/" in p:
                print(p)
                sub_mod_map = recScanSource(p, {})
                for v in sub_mod_map.keys():
                    mod_map[v] = sub_mod_map[v]

        return mod_map

    mod_map: dict[str, str] = recScanSource(f"./{source_dir}/{entry}", {})

    for key in mod_map.keys():
        print(key, mod_map[key])

    if not path.exists(f"./{build_dir}"):
        mkdir(f"./{build_dir}")

    if not path.exists(f"./{build_dir}/ext"):
        mkdir(f"./{build_dir}/ext")

    # Copy the source files to build dir
    for key in mod_map.keys():
        if not f"./{source_dir}/" in mod_map[key]:
            copy_path = mod_map[key].split("/")[:-1]
            mod_dir = copy_path[-1]
            out_dir = f"./{build_dir}/ext/{mod_dir}"
            if path.exists(out_dir):
                rmtree(out_dir)
            copytree("/".join(copy_path), f"./{build_dir}/ext/{mod_dir}")
            print("Copied", mod_map[key])
            no_init = "init.lua" not in listdir(f"./{build_dir}/ext/{mod_dir}")
            # If there module is a *.so, create an init
            if mod_map[key].endswith(".so"):
                init_lua_content = init_lua_template_so.replace("{mod}", key)
                with open(f"./{build_dir}/ext/{mod_dir}/init.lua", "w") as init_file:
                    init_file.writelines(init_lua_content.splitlines(keepends=True))
                print(f"Wrote init.lua for {mod_dir}.so")
            # If there's no init, rename the main source file
            elif no_init:
                init_lua_content = init_lua_template_lua.replace("{mod}", key)
                with open(f"./{build_dir}/ext/{mod_dir}/init.lua", "w") as init_file:
                    init_file.writelines(init_lua_content.splitlines(keepends=True))
                print(f"Wrote init.lua for {mod_dir}.lua")

    def recCompile(directory: str):
        """
        Compile the project source directory.
        """
        dir_list = listdir(directory)

        for dir in dir_list:
            full_path = directory + "/" + dir
            if path.isdir(full_path):
                print(full_path)
                recCompile(full_path)
            else:
                with open(full_path, "rb") as dat:
                    tree: ast.Chunk = pload(dat)

                comped = ast.to_lua_source(tree)

                comped = sub(r"\s+\(", "(", comped)

                for mod in mod_map.keys():
                    if not f"./{source_dir}/" in mod_map[mod]:
                        comped = comped.replace(
                            f'require("{mod}', f'require("ext.{mod}'
                        )
                        comped = comped.replace(
                            f"require('{mod}", f"require('ext.{mod}"
                        )

                out_dir = full_path.split("/")
                comp_path = "/".join([f"./{build_dir}"] + out_dir[2:]).replace(
                    ".dat", ".lua"
                )
                if len(out_dir) > 2 and not out_dir[1].endswith(".dat"):
                    for i in range(2, len(out_dir) - 1):
                        tmp = "/".join(out_dir[2 : i + 1])
                        if not path.exists(f"./{build_dir}/{tmp}"):
                            mkdir(f"./{build_dir}/{tmp}")

                with open(comp_path, "w") as out:
                    out.write(comped)
                print("Built", comp_path)
        return

    recCompile("./.bld")

    def recRegisterAssets(dir: str, asset_dict={}):
        """
        Register assets in the project source based on the build.include pattern
        list.
        """
        print(f"Checking {dir}...")
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
                copyfile(f"./{source_dir}/{dir}/{key}", f"./{build_dir}/{dir}/{key}")
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
