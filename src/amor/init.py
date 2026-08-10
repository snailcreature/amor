from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def init(
    project_name: Annotated[
        str | None, typer.Argument(help="The name of the project.")
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force/",
            "-f/",
            help="Force the creation of a fresh amor.toml config file.",
        ),
    ] = False,
    git_init: Annotated[
        bool, typer.Option("--git-init/", "-g/", help="Initialise git in project")
    ] = False,
):
    """
    Initialise an amor project in the current directory.
    """
    from toml import load, dump
    from json import dump as jdump
    from git import Repo
    from os import listdir
    from typing import cast
    from rich import print

    from .types import AmorConfig
    from .constants import default_conf, gitignore_lines, gitattributes_lines, luarc

    with open("amor.toml", "r") as conf:
        amor_conf: AmorConfig = cast(AmorConfig, load(conf))

    if not force and len(amor_conf.keys()) != 0:
        print(
            "[yellow]amor.toml already exists!\nRun with --force to reset the config\
              file"
        )
        return

    amor_conf = default_conf

    print("[blue]Creating amor.toml...")
    if project_name is not None and len(project_name) > 0:
        amor_conf["project"]["name"] = project_name

    with open("amor.toml", "w") as conf:
        dump(amor_conf, conf)

    luarc_exists = ".luarc.json" in listdir("./")
    if not luarc_exists:
        print("[blue]Creating .luarc.json...")
        with open(".luarc.json", "w") as luarc_file:
            jdump(luarc, luarc_file)

    if git_init:
        print("[blue]Creating .gitignore...")
        with open(".gitignore", "w") as gitignore:
            gitignore.writelines(gitignore_lines)

        print("[blue]Creating .gitattributes")
        with open(".gitattributes", "w") as gitattributes:
            gitattributes.writelines(gitattributes_lines)

        print("[blue]Initialising git repo...")
        repo = Repo.init(".")
        repo.index.add([".gitattributes", ".gitignore", "amor.toml", ".luarc.json"])

    print("[green]Project initialised!")

    return
