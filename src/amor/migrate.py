import typer

app = typer.Typer()


@app.command()
def migrate():
    """
    Migrates the current project to a newer version of amor
    """
    from toml import load as tload, dump as tdump
    from json import load as jload, dump as jdump
    from os import path
    from typing import cast
    from re import split
    from rich import print
    from rich.progress import Progress
    from .types import (
        AmorConfigDependencies,
        AmorLock,
        AmorOldConfigDependency,
        AmorVersion,
    )
    from .__init__ import __version__

    with open("amor.toml", "r") as conf:
        amor_conf: dict = tload(conf)

    try:
        current_version: AmorVersion = amor_conf["amor_version"]
    except KeyError:
        current_version: AmorVersion = None

    if current_version is None:
        print("Detected version 0.4.0 or earlier...")
    else:
        print(f"Detected version {current_version}...")
    print(f"Migrating to version {__version__}")

    while True:
        match current_version:
            case None:
                # Update .luarc.json
                try:
                    with open(".luarc.json", "r") as rc:
                        luarc: dict = jload(rc)
                except:
                    luarc: dict = {}

                luarc["$schema"] = (
                    "https://raw.githubusercontent.com/LuaLS/vscode-lua/master/setting/schema.json"
                )
                if "workspace" not in luarc.keys():
                    luarc["workspace"] = {}

                if "library" not in luarc["workspace"].keys():
                    luarc["workspace"]["library"] = []

                if "${workspaceFolder}/.amor/" not in luarc["workspace"]["library"]:
                    luarc["workspace"]["library"].append("${workspaceFolder}/.amor/")

                # Create amor.lock
                deps = cast(dict[str, str], amor_conf["dependencies"])
                new_deps: AmorConfigDependencies = {}
                lock: AmorLock = {}
                module_split = r"\/|\@|\="
                with Progress() as progress:
                    task = progress.add_task(
                        "Creating amor.lock...", total=len(deps.keys())
                    )
                    for mod in deps.keys():
                        mod_author, mod_name, mod_tag, mod_hash = cast(
                            AmorOldConfigDependency, split(module_split, deps[mod])
                        )
                        if mod_tag == "None":
                            mod_tag = None
                        lock[mod_name] = {
                            "version": mod_tag,
                            "hash": mod_hash,
                            "src": f"https://github.com/{mod_author}/{mod_name}.git",
                            "author": mod_author,
                        }
                        if mod_tag is None or mod_tag == "None":
                            new_deps[mod_name] = {
                                "src": f"https://github.com/{mod_author}/{mod_name}.git",
                                "version": None,
                            }
                        else:
                            new_deps[mod_name] = mod_tag
                        progress.advance(task)

                amor_conf["dependencies"] = new_deps

                current_version = "0.5.0"
                with open(".luarc.json", "w") as rc:
                    jdump(luarc, rc, indent=4)

                with open("amor.lock", "w") as al:
                    tdump(lock, al)

                amor_conf["project"]["amor_version"] = current_version
                with open("amor.toml", "w") as conf:
                    tdump(amor_conf, conf)
            case _:
                print("You're all up to date!")
                break
