from typing import Annotated

import typer
from .new import app as newOpt
from .init import app as initOpt
from .install import app as installOpt
from .uninstall import app as uninstallOpt
from .run import app as runOpt
from .build import app as buildOpt
from .love import app as loveOpt
from .migrate import app as migrateOpt
from .__init__ import __version__

app = typer.Typer(
    no_args_is_help=True, help="A package manager for the Löve game engine."
)

app.add_typer(newOpt)
app.add_typer(initOpt)
app.add_typer(installOpt)
app.add_typer(uninstallOpt)
app.add_typer(runOpt)
app.add_typer(buildOpt)
app.add_typer(loveOpt)
app.add_typer(migrateOpt)


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


if __name__ == "__main__":
    app()
