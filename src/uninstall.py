from typing import Annotated

import typer

app = typer.Typer()

@app.command()
def uninstallOpt(module: Annotated[list[str], typer.Argument(help="Module(s) to\
        uninstall, given in format `<module_name>` (as you would require\
        in a Lua script).")]):
    """
    Uninstall the given module(s) from the project.
    """

    if len(module) == 0:
        print("You must provide at least 1 module to uninstall.")
        raise typer.Exit()

    from toml import load, dump
    from shutil import rmtree
    
    with open('amor.toml', 'r') as amor_conf:
        conf = load(amor_conf)

    deps: dict[str, str] = conf["dependencies"]

    to_delete: list[str] = [dep for dep in deps if dep in module]

    for dep in to_delete:
        print(f'Uninstalling {dep}')
        try:
            rmtree(f'./.amor/{dep}')

            del conf["dependencies"][dep]
        except:
            print(f'Failed to uninstall {dep}.') 
    
    with open('amor.toml', 'w') as amor_conf:
        dump(conf, amor_conf)

    return


