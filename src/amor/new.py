from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def new(
    name: Annotated[
        str,
        typer.Argument(
            help="The name of the project. A directory with this name will be created."
        ),
    ],
    git_init: Annotated[
        bool,
        typer.Option("--git-init/", "-g/", help="Initialise git in project"),
    ] = False,
):
    """
    Create a new project folder.
    """
    from os import mkdir, path, environ
    from shutil import copytree
    from toml import dump
    from git import Repo
    from rich import print

    from .constants import (
        default_conf,
        main_lua_content,
        gitignore_lines,
        gitattributes_lines,
        luarc,
    )

    if name == ".":
        print(
            "[yellow]Please run `amor init` to start your project in the current\
                directory."
        )
        return

    conf = default_conf

    conf["project"]["name"] = name

    print("[blue]Making directory ./" + name + "...")
    mkdir("./" + name)
    mkdir("./" + name + "/src")
    with open("./" + name + "/src/main.lua", "w") as main_lua:
        main_lua.writelines(main_lua_content)

    print("[blue]Creating ./" + name + "/amor.conf...")
    with open("./" + name + "/amor.toml", "w") as conf_file:
        dump(conf, conf_file)

    print("[blue]Creating ./" + name + "/.luarc.json...")
    with open(f"./{name}/.luarc.json", "w") as luarc_file:
        luarc_file.writelines(luarc)

    mkdir("./.amor/")
    mkdir("./.amor/builtin/")
    amor_dir = environ.get("AMOR_DIR")
    if amor_dir is not None:
        copytree(f"{amor_dir}/lsp/", "./.amor/builtin/")
    else:
        print("[yellow]AMOR_DIR is not set, so could not copy löve definitions")

    if git_init:
        print("[blue]Creating .gitignore...")
        with open("./" + name + "/.gitignore", "w") as gitignore:
            gitignore.writelines(gitignore_lines)

        with open("./" + name + "/.gitattributes", "w") as gitattributes:
            gitattributes.writelines(gitattributes_lines)

        print("[blue]Initialising git repo...")
        repo = Repo.init(path.join(name))
        repo.index.add([".gitignore", ".gitattributes", "amor.toml", ".luarc.json"])
        repo.index.commit("Initial commit")

    print("[green]New project", name, "created!")
    return
