from typing import Annotated

import typer
from src.new import app as newOpt
from src.init import app as initOpt
from src.install import app as installOpt
from src.uninstall import app as uninstallOpt
from src.run import app as runOpt
from src.build import app as buildOpt
from src.love import app as loveOpt

# amor version
__version__ = '0.5.0'
__author__ = 'Sam Drage (github: snailcreature)'
__date__ = '2026-08-06'

app = typer.Typer(no_args_is_help=True, \
        help="A package manager for the Löve game engine.")

app.add_typer(newOpt)
app.add_typer(initOpt)
app.add_typer(installOpt)
app.add_typer(uninstallOpt)
app.add_typer(runOpt)
app.add_typer(buildOpt)
app.add_typer(loveOpt)

@app.command()
def version():
    """
    Display the current amor version.
    """
    print(f"amor {__version__}")

if __name__ == "__main__":
    app()
