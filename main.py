from typing import Annotated, Optional

import typer
from src.amor.new import app as newOpt
from src.amor.init import app as initOpt
from src.amor.install import app as installOpt
from src.amor.uninstall import app as uninstallOpt
from src.amor.run import app as runOpt
from src.amor.build import app as buildOpt
from src.amor.love import app as loveOpt
from src.amor import __version__

app = typer.Typer(
    no_args_is_help=False, help="A package manager for the Löve game engine."
)


@app.callback(invoke_without_command=True)
def callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version/",
            "-v/",
            is_eager=True,
            help="Display the current version of amor",
        ),
    ] = False,
):
    """
    Display the current amor version.
    """
    if version:
        print(f"amor {__version__}")
        raise typer.Exit()


app.add_typer(newOpt)
app.add_typer(initOpt)
app.add_typer(installOpt)
app.add_typer(uninstallOpt)
app.add_typer(runOpt)
app.add_typer(buildOpt)
app.add_typer(loveOpt)

if __name__ == "__main__":
    app()
