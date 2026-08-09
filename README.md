# amor: A Löve2D project manager :heart:

As a package and project manager, amor can:

- Create a new Löve project
- Initialise in an existing Löve project
- Install and build modules from GitHub
- Track your installed modules for project set up and recovery
- Build your project into a single directory including:
    - Your source files
    - Assets you have flagged
    - External modules you have installed
- Run custom scripts

## About

Written in Python, amor aims to provide a lightweight solution to
the issue of creating, managing, and building [Löve](https://love2d.org/)
projects. It uses [GitPython](https://gitpython.readthedocs.io/en/stable/) to
install modules, and a combination of [luaparser](https://pypi.org/project/luaparser/)
and [lupa](https://pypi.org/project/lupa/) to build the final project. A toml
configuration file is used for easy management of project settings and
dependencies.

amor requires [git](https://git-scm.com/downloads), [luarocks](https://luarocks.org/),
and some version of gnu-make be installed, along with Lua (5.4 preferred). 
[Löve](https://love2d.org/) is also required.

This is a hobby project that is maintained by an individual. Please submit any
bugs you find as Issues. Check [the Changelog](/CHANGELOG.md) before updating.

## Requirements

 - [Python3](https://www.python.org/downloads/) (Python 3.14 or later) - For amor itself
 - [git](https://git-scm.com/) - For downloading packages
 - [LuaRocks](https://luarocks.org/) - For building some packages
 - [cmake](https://cmake.org/) - For building some other packages
 - [Löve](https://www.love2d.org/) - For making your game

## Setup

To run the automatic install script:

```shell
curl --proto '=https' -sSf https://raw.githubusercontent.com/snailcreature/amor/refs/heads/main/install.sh | bash
```

Installs the amor source to `~/.local/share/amor`.

Subsequent runs of this script will produce a fresh installation.

### Manual Install

Clone this repository then run

```shell
bash ./setup.sh
```

or,

```shell
chmod +x ./setup
./setup.sh
```

This will create the stand-alone executable version of amor and install it to your Python binaries, allowing you to run it anywhere.

## Usage

Open a terminal in your development folder and run

```shell
amor new my_project -g
```

This will create a new project in the folder `my_project` with git initialised,
along with a default `amor.toml` and `src` directory with a `main.lua`
pre-configured with the core Löve functions (load, update, and draw).

Run `amor --help` for a full list of commands and how to use them.

## Updating

Go to your cloned version of this project and run

```shell
git pull
bash setup # or "./setup", if you ran "chmod +x ./setup" before
```

Please check [the Changelog](/CHANGELOG.md) for breaking changes before
updating.

> [!IMPORTANT] Once you have updated, be sure to run `amor migrate` in any active projects. This will apply patches to bring a project up-to-date with the currently-installed
> amor version

## Credits

Example `tilemap.png` created by [Kenney](kenney.nl) (CC0).

No AI was knowingly used in the research or creation of this tool.

## Roadmap

- [ ] Incremental builds
- [ ] Dev dependencies
- [ ] Dependency execution
- [ ] Non-Github installs
    - [ ] Codeberg
    - [ ] Forgejo
    - [ ] Gitlab
    - [ ] Luarocks
