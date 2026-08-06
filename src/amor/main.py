from typing import Annotated

import typer
from .new import app as newOpt
from .init import app as initOpt
from .install import app as installOpt
from .uninstall import app as uninstallOpt
from .run import app as runOpt
from .build import app as buildOpt
from .love import app as loveOpt
from .__init__ import __version__

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

