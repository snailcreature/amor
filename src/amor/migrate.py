import typer

from amor.types import AmorConfigDependencies, AmorLock

app = typer.Typer()


@app.command()
def migrate():
    """
    Migrates the current project to a newer version of amor
    """
    from toml import load as tload, dump as tdump
    from json import load as jload, dumps as jdumps
    from os import path
    from typing import cast
    from .types import AmorVersion
    from .__init__ import __version__

    with open("amor.toml", "r") as conf:
        amor_conf: dict = tload(conf)

    current_version: AmorVersion = amor_conf["amor_version"]
    if current_version is None:
        print("Detected version 0.4.0 or earlier...")
    else:
        print(f"Detected version {current_version}...")
    print(f"Migrating to version {__version__}")

    while True:
        match current_version:
            case None:
                # Update .luarc.json
                with open(".luarc.json", "r") as rc:
                    luarc: dict = jload(rc)

                luarc["$schema"] = (
                    "https://raw.githubusercontent.com/LuaLS/vscode-lua/master/setting/schema.json"
                )
                if luarc["workspace"] is None:
                    luarc["workspace"] = {}

                if luarc["workspace"]["library"] is None:
                    luarc["workspace"]["library"] = []

                if "${workspaceFolder}/.amor/" not in luarc["workspace"]["library"]:
                    luarc["workspace"]["library"].append("${workspaceFolder}/.amor/")

                # Create amor.lock
                deps = cast(dict[str, str], amor_conf["dependencies"])
                new_deps: AmorConfigDependencies = {}
                lock: AmorLock = {}
                for mod in deps.keys():
                    mod_name_tag, mod_hash = deps[mod].split("=")
                    mod_author_name, mod_tag = mod_name_tag.split("@")
                    new_deps[mod_author_name] = mod_tag
                    mod_name, mod_author = mod_author_name.split("/")
                    lock[mod_name] = {
                        "version": mod_tag,
                        "hash": mod_hash,
                        "src": f"https://github.com/{mod_author_name}.git",
                        "author": mod_author,
                    }

                amor_conf["dependencies"] = new_deps

                current_version = "0.5.0"
                with open(".luarc.json", "w") as rc:
                    rc.write(jdumps(luarc, indent=4))

                with open("amor.lock", "w") as al:
                    tdump(lock, al)

                amor_conf["project"]["amor_version"] = current_version
                with open("amor.toml", "w") as conf:
                    tdump(amor_conf, conf)
            case _:
                print("You're all up to date!")
                break
