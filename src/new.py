from argparse import Namespace

def newOpt(args: Namespace):
    """
    Create a new repository from scratch.
    """
    from os import mkdir, path
    from toml import dump
    from git import Repo

    from constants import default_conf, main_lua_content, gitignore_lines,\
    gitattributes_lines, luarc
    
    name = args.name[0]
     
    if name == '.':
        print("Please run `amor init` to start your project in the current\
                directory.")
        return

    conf = default_conf

    conf["project"]["name"] = name
    
    print("Making directory ./"+name+"...")
    mkdir('./'+name)
    mkdir('./'+name+'/src')
    with open('./'+name+'/src/main.lua', 'w') as main_lua:
        main_lua.writelines(main_lua_content)

    print("Creating ./"+name+"/amor.conf...")
    with open('./'+name+'/amor.toml', 'w') as conf_file:
        dump(conf, conf_file)

    print("Creating ./"+name+"/.luarc.json...")
    with open(f"./{name}/.luarc.json", 'w') as luarc_file:
        luarc_file.writelines(luarc)

    if args.git_init:
        print("Creating .gitignore...")
        with open("./"+name+"/.gitignore", 'w') as gitignore:
            gitignore.writelines(gitignore_lines)

        with open("./"+name+"/.gitattributes", 'w') as gitattributes:
            gitattributes.writelines(gitattributes_lines)

        print("Initialising git repo...")
        repo = Repo.init(path.join(name))
        repo.index.add([".gitignore",
                ".gitattributes",
                "amor.toml"
            ])
        repo.index.commit("Initial commit")
    
    print("New project", name, "created!")
    return


