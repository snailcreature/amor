from argparse import Namespace
from toml import load, dump
from git import Repo

from constants import default_conf, gitignore_lines, gitattributes_lines

def initOpt(args: Namespace):
    """
    Initialise amor in the current repository.
    """
    with open('amor.toml', 'r') as conf:
        amor_conf: dict = load(conf)

    if not args.force and len(amor_conf.keys()) != 0:
        print('amor.toml already exists!\nRun with --force to reset the config\
              file')
        return

    amor_conf = default_conf
    
    print("Creating amor.toml...")
    if args.project_name != None:
        amor_conf["project"]["name"] = args.project_name

    with open('amor.toml', 'w') as conf:
        dump(amor_conf, conf)

    if args.git_init:
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


