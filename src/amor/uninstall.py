from typing import Annotated

import typer

app = typer.Typer()


@app.command("u", hidden=True)
@app.command("remove", hidden=True)
@app.command()
def uninstall(
    modules: Annotated[
        list[str],
        typer.Argument(
            min=1,
            help="""
Module(s) to uninstall, given in format `<module_name>` (as you would require \
in a Lua script).""",
        ),
    ],
):
    """
    Uninstall the given module(s) from the project.
    (Aliases: `u`, `remove`)
    """
    from rich import print

    if len(modules) == 0:
        print("[red]You must provide at least 1 module to uninstall.")
        raise typer.Exit()

    from toml import load, dump
    from shutil import rmtree

    with open("amor.toml", "r") as amor_conf:
        conf = load(amor_conf)

    with open("amor.lock", "r") as amor_lock:
        lock = load(amor_lock)

    deps: dict[str, str] = conf["dependencies"]

    to_delete: list[str] = [dep for dep in deps.keys() if dep in modules]
    lock_clean: list[str] = [dep for dep in lock.keys() if dep not in deps.keys()]

    for dep in to_delete:
        print(f"Uninstalling {dep}")
        try:
            rmtree(f"./.amor/{dep}")

            del conf["dependencies"][dep]
            del lock[dep]
        except:
            print(f"[red]Failed to uninstall {dep}.")

    if len(lock_clean) > 0:
        print("Cleaning up lock file...")
        for dep in lock_clean:
            try:
                rmtree(f"./.amor/{dep}")

                del lock[dep]
            except:
                print(f"[red]Failed to clean {dep}.")

    with open("amor.toml", "w") as amor_conf:
        dump(conf, amor_conf)

    with open("amor.lock", "w") as amor_lock:
        dump(lock, amor_lock)

    return
