from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def run(script: Annotated[str, typer.Argument(help="Name of script to run.")]):
    """
    Run a given script name from the project amor.toml.
    """
    from toml import load
    from subprocess import PIPE, run as cmd

    script = script
    with open("amor.toml", "r") as conf:
        amor_conf: dict = load(conf)

    scripts: dict = amor_conf["scripts"]

    if script not in scripts.keys():
        print(script, "not defined!")
        return

    parts: list[str] = scripts[script].split(" && ")
    print("Running script", scripts[script])
    for part in parts:
        print(">", part)
        res = cmd(part.split(" "), stdout=PIPE, text=True)

        for line in res.stdout.splitlines():
            print(line)

        res.check_returncode()
    return
