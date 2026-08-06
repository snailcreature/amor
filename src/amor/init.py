from typing import Annotated

import typer

app = typer.Typer()

@app.command()
def init(project_name: Annotated[str | None, typer.Argument(help="The name of the project.")] = None, \
        force: Annotated[bool, typer.Option(help="Force the creation of a fresh amor.toml config file.")] = False, \
        no_git: Annotated[bool, typer.Option(help="Do not initialise git in project")] = False):
    """
    Initialise an amor project in the current directory.
    """
    from toml import load, dump
    from git import Repo
    from os import listdir

    from constants import default_conf, gitignore_lines, gitattributes_lines,\
            luarc
    
    with open('amor.toml', 'r') as conf:
        amor_conf: dict = load(conf)

    if not force and len(amor_conf.keys()) != 0:
        print('amor.toml already exists!\nRun with --force to reset the config\
              file')
        return

    amor_conf = default_conf
    
    print("Creating amor.toml...")
    if project_name != None and len(project_name) > 0:
        amor_conf["project"]["name"] = project_name

    with open('amor.toml', 'w') as conf:
        dump(amor_conf, conf)
    
    print("Creating .luarc.json...")
    luarc_exists = ".luarc.json" in listdir('./')
    if not luarc_exists:
        with open('.luarc.json', 'w') as luarc_file:
            luarc_file.writelines(luarc)

    if not no_git:
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


