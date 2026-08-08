import typer

app = typer.Typer()


@app.command()
def migrate():
    """
    Migrates the current project to a newer version of amor
    """
    from toml import load as tload, dump as tdump
    from json import load as jload, dumps as jdumps
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
                with open(".luarc.json", "r") as rc:
                    luarc: dict = jload(rc)

                if luarc["workspace"] is None:
                    luarc["workspace"] = {}

                if luarc["workspace"]["library"] is None:
                    luarc["workspace"]["library"] = []

                if "${workspaceFolder:.amor}" not in luarc["workspace"]["library"]:
                    luarc["workspace"]["library"].append("${workspaceFolder:.amor}")

                with open(".luarc.json", "w") as rc:
                    rc.write(jdumps(luarc, indent=4))

                current_version = "0.5.0"
                amor_conf["project"]["amor_version"] = current_version
                with open("amor.toml", "w") as conf:
                    tdump(amor_conf, conf)
            case _:
                print("You're all up to date!")
                break
