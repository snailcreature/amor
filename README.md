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
the issue of creating, managing, and building Löve projects. It uses
GitPython to install modules, and a combination of luaparser and lupa to
build the final project. A toml configuration file is used for easy management
of project settings and dependencies.

amor requires [git](https://git-scm.com/downloads), [luarocks](https://luarocks.org/),
and some version of gnu-make be installed, along with Lua (5.4 preferred). 
[Löve](https://love2d.org/) is also required.

This is a hobby project that is maintained by an individual. Please submit any
bugs you find as Issues. Check [the Changelog](/CHANGELOG.md) before updating.

## Setup

Clone this repository then run

```shell
bash setup

# Or

chmod +x ./setup
./setup
```

This will create the standalone executable version of amor. Add the path
to your system PATH to be able to run it from anywhere on your system.

## Usage

Open a terminal in your development folder and run

```shell
amor new my_project -g
```

This will create a new project in the folder `my_project` with git initialised,
along with a default `amor.toml` and `src` directory with a `main.lua`
pre-configured with the core Löve functions (load, update, and draw).

Run `amor -h` for a full list of commands and how to use them.

## Updating

Go to your cloned version of this project and run

```shell
git pull
./setup
```

Please check [the Changelog](/CHANGELOG.md) for breaking changes before
updating.

## Credits

Example `tilemap.png` created by [Kenney](kenney.nl) (CC0).

## Roadmap

- [ ] Incremental builds
- [ ] Dev dependencies
- [ ] Dependency execution
