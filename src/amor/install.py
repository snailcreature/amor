from typing import Annotated
import typer

app = typer.Typer()


@app.command("i", hidden=True)
@app.command("add", hidden=True)
@app.command()
def install(
    module: Annotated[
        list[str] | None,
        typer.Argument(
            help="""
Module(s) to install from Github. Given in format '<username>/<repository>(@<tag>)'. \
If <tag> is not present the most current version will be installed. If <tag> is \
present, but does not exist on repository, the most current version will be installed.""",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force/", "-f/", help="Force the re-installation of all modules."
        ),
    ] = False,
):
    """
    Install given repositor(y/ies) or all repositories in the project amor.toml.
    (Aliases: `i`, `add`)
    """
    from re import split as resplit
    from os import listdir, path, getcwd, environ
    from shutil import rmtree, copytree
    from toml import load, dump
    from git import Repo
    from subprocess import PIPE, run as cmd
    from typing import cast
    from rich import print
    from rich.progress import open as ropen, Progress

    try:
        from lupa.lua54 import LuaRuntime
    except ImportError:
        try:
            from lupa.lua53 import LuaRuntime
        except ImportError:
            try:
                from lupa.lua52 import LuaRuntime
            except ImportError:
                from lupa.lua51 import LuaRuntime

    from .utils import (
        getRepoHeadHash,
        getRepoTagHashes,
        include_patterns,
        remove_empty_dirs,
        get_gh_repo_info,
        github_url_split_regex,
        install_module_split,
    )
    from amor.types import (
        AmorConfig,
        AmorConfigDependency,
        AmorConfigDependencies,
        AmorLock,
        AmorLockEntry,
        AmorInstallMod,
    )

    hashes: dict[str, str] = {}

    modules: dict[str, AmorConfigDependency] = {}

    if force:
        for dir in listdir("./.amor"):
            try:
                rmtree(f"./.amor/{dir}/")
            except:
                print(f"Failed to delete {dir}")
                raise typer.Exit(1)

    with ropen("amor.lock", "r", description="Reading amor.lock...") as amor_lock:
        lock: AmorLock = load(amor_lock)

    # If no modules given, install from .toml and .lock
    with Progress() as p:
        if module is None:
            with ropen(
                "amor.toml", "r", description="Reading from amor.toml..."
            ) as amor_conf:
                conf: AmorConfig = cast(AmorConfig, load(amor_conf))

            task = p.add_task(
                "Processing dependencies...", total=len(conf["dependencies"].keys())
            )
            for package in conf["dependencies"].keys():
                entry = conf["dependencies"][package]
                locked: AmorLockEntry | None = lock[package]
                version: str | None
                repo: str
                src: str
                if locked is None:
                    if type(entry) is str:
                        p.console.print(
                            f"Please provide a source for {package} in your amor.toml"
                        )
                        p.console.print(f"Skipping {package}")
                        p.advance(task)
                        continue
                    else:
                        if entry["src"] is not None:
                            author, proj = re.split(
                                github_url_split_regex, entry["src"]
                            )
                            repo = f"{author}/{proj}"
                            src = entry["src"]
                        else:
                            p.console.print(
                                f"Please provide a source for {mod} in your amor.toml"
                            )
                            p.console.print(f"Skipping {mod}")
                            p.advance(task)
                            continue

                        version = entry["version"]
                else:
                    author = locked["author"]
                    src = locked["src"]
                    repo = f"{author}/{package}"
                    try:
                        if locked["version"] == "None":
                            version = None
                    except KeyError:
                        version = None
                    else:
                        version = locked["version"]
                    hashes[package] = locked["hash"]
                modules[package] = {
                    "src": src,
                    "version": version,
                }
                p.console.print(f"{repo}@{version}")
                p.advance(task)
            p.remove_task(task)
        else:
            task = p.add_task("Processing modules...", total=len(module))
            for m in module:
                author, package, tag = cast(
                    AmorInstallMod, resplit(install_module_split, m)
                )
                modules[package] = {
                    "src": f"https://github.com/{author}/{package}.git",
                    "version": tag,
                }
                p.advance(task)
            p.remove_task(task)

    with Progress() as p:
        task = p.add_task("Installing...", total=len(modules.keys()))
        for package in modules.keys():
            p.console.print("Installing", package + "...")
            if path.exists("./.amor/tmp/"):
                rmtree("./.amor/tmp/")

            mod = modules[package]
            tag = mod["version"]
            mod_name = package

            git_url = cast(str, mod["src"])
            tags = getRepoTagHashes(git_url)
            _, mod_author = get_gh_repo_info(git_url)

            hash: str
            if tag is not None and tag in tags.keys():
                hash = tags[tag]
            else:
                hash = getRepoHeadHash(git_url)
            p.console.print(tag, hash)
            if tag is None:
                print(f"{package} tag is None")
            if tag == "None":
                print(f"{package} tag is 'None'")

            if len(hashes.keys()) > 0:
                try:
                    r = Repo.clone_from(git_url, to_path="./.amor/tmp/", branch=tag)
                    r.index.reset(commit=hashes[package], working_tree=True)
                except KeyError:
                    p.console.print("Something went wrong resetting the HEAD!")
                    p.console.print("Proceeding with cloned HEAD...")
            else:
                Repo.clone_from(git_url, to_path="./.amor/tmp/", branch=tag, depth=1)

            dir_content = listdir("./.amor/tmp")
            rockspecs = [file for file in dir_content if file.endswith(".rockspec")]
            makefiles = [file for file in dir_content if "Makefile" in file]

            built_from_spec = False
            built_from_rockspec = False
            built_from_makefile = False
            try:
                if len(rockspecs) > 0:
                    p.console.print("Building from Rockspec...")
                    res = cmd(
                        [
                            "luarocks",
                            "build",
                            rockspecs[0],
                            f'--tree="build"',
                        ],
                        cwd="./.amor/tmp/",
                        stdout=PIPE,
                        text=True,
                    )

                    for line in res.stdout.splitlines():
                        console.print(line)

                    res.check_returncode()

                    with open(f"./.amor/tmp/{rockspecs[0]}", "r") as rs:
                        rspec = rs.readlines()

                    rspec.append(
                        "if build and package then return { package = package,\
                                                               modules = build.modules} end\n"
                    )
                    lua = LuaRuntime(unpack_returned_tuples=False)
                    build_modules = dict(lua.execute("".join(rspec)))  # type: ignore
                    p.console.print(build_modules)
                    mods: list[str] = [mod for mod in build_modules["modules"]]  # type: ignore
                    build_package: str | None = build_modules["package"]  # type: ignore

                    p.console.print(*mods)
                    console.print(build_modules["package"])  # type: ignore
                    has_package = build_package is not None
                    renamed_mod = list(filter(lambda m: "." not in m, mods))
                    mismatch_module_name = (
                        len(renamed_mod) != 0 and build_package not in renamed_mod
                    )
                    p.console.print(*renamed_mod)

                    if has_package:
                        p.console.print("has package", build_package)
                        mod_name = build_package
                    if mismatch_module_name:
                        p.console.print("but has mismatch", renamed_mod[0])
                        mod_name = renamed_mod[0]
                    if not has_package and not mismatch_module_name and len(mods) > 0:
                        p.console.print("fallback")
                        mod_name = mods[0]

                    mod_name = cast(str, mod_name)

                    if path.exists(f"./.amor/{mod_name}"):
                        rmtree(f"./.amor/{mod_name}")

                    cwd = getcwd()
                    try:
                        copytree(
                            f"{cwd}/.amor/tmp/build/lib/lua/5.4/",
                            f"{cwd}/.amor/{mod_name}/",
                        )
                    except:
                        p.console.print(
                            "Default build location not found, trying fallback..."
                        )
                        try:
                            copytree(
                                f"{cwd}/.amor/tmp/build/share/lua/5.4/{mod_name}/",
                                f"{cwd}/.amor/{mod_name}/",
                            )
                        except:
                            p.console.print(f"Uh oh! {mod_name} could not be built!")
                            raise
                    built_from_rockspec = True

                elif len(makefiles) > 0:
                    p.console.print("Building from Makefile...")
                    for makefile in makefiles:
                        with ropen(
                            f"./.amor/tmp/{makefile}",
                            "r",
                            description="Reading makefile...",
                        ) as mf:
                            lines = mf.readlines()

                        for i in range(len(lines)):
                            if "config" in lines[i] or "CONFIG" in lines[i]:
                                lines[i] = f"# {lines[i]}"

                        with open(f"./.amor/tmp/{makefile}", "w") as mf:
                            mf.writelines(lines)

                    LUA_INCLUDE = environ.copy()["LUA_INCLUDE"]
                    p.console.print(LUA_INCLUDE)
                    res = cmd(
                        ["make", f"--include-dir={LUA_INCLUDE}"],
                        stdout=PIPE,
                        shell=True,
                        text=True,
                        cwd="./.amor/tmp/",
                    )

                    for line in res.stdout.splitlines():
                        print(line)

                    res.check_returncode()
                    built_from_makefile = True
            except:
                p.console.print(
                    "Something went wrong whilst building, attempting source \
                      copy..."
                )
            else:
                p.console.print("No errors!")
                built_from_spec = built_from_rockspec or built_from_makefile
            finally:
                p.console.print("Final checks...")
                if not built_from_spec:
                    p.console.print("No build option found! Copying files...")

                    if path.exists(f"./.amor/{mod_name}"):
                        rmtree(f"./.amor/{mod_name}")

                    copytree(
                        "./.amor/tmp",
                        f"./.amor/{mod_name}",
                        ignore=include_patterns("*.lua", "*.so"),
                    )

                    remove_empty_dirs(f"./.amor/{mod_name}/")

            rmtree("./.amor/tmp")

            with open("amor.toml", "r") as amor_conf:
                conf: AmorConfig = cast(AmorConfig, load(amor_conf))

            if conf["dependencies"] is None:
                conf["dependencies"] = {}

            mod_entry: AmorConfigDependency | str
            if tag is None:
                mod_entry = {"src": git_url, "version": None}
            else:
                mod_entry = tag
            conf["dependencies"][mod_name] = mod_entry

            lock[mod_name] = {
                "src": git_url,
                "version": tag,
                "hash": hash,
                "author": mod_author,
            }

            with open("amor.toml", "w") as amor_conf:
                dump(conf, amor_conf)

            with open("amor.lock", "w") as amor_lock:
                dump(lock, amor_lock)

            p.console.print(f"Installed {mod_name}!")
            p.advance(task)
        p.remove_task(task)
    return
