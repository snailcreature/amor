from argparse import ArgumentParser, Namespace

# amor version
__version__ = '0.5.0'
__author__ = 'Sam Drage (github: snailcreature)'
__date__ = '2026-08-06'

def _newOpt(args: Namespace):
    from new import newOpt
    newOpt(args)

def _initOpt(args: Namespace):
    from init import initOpt
    initOpt(args)

def _installOpt(args: Namespace):
    from install import installOpt
    installOpt(args)

def _uninstallOpt(args: Namespace):
    from uninstall import uninstallOpt
    uninstallOpt(args)

def _runOpt(args: Namespace):
    from run import runOpt
    runOpt(args)

def _loveOpt(args: Namespace):
    from love import loveOpt
    loveOpt(args)

def _buildOpt(args: Namespace):
    from build import buildOpt
    buildOpt(args)



def defaultOpt(args: Namespace):
    if args.version:
        print(f"amor {__version__}")
    return


# Parser
parser = ArgumentParser(description="A package manager for the Löve game\
                        engine.")

parser.add_argument('--version', '-v', action="store_true", help="Show the\
        installed amor version.")
parser.set_defaults(func=defaultOpt)

subparsers = parser.add_subparsers(help="Additional commands")

# New
newParse = subparsers.add_parser("new", help="Create a new project folder.")
newParse.add_argument("name", nargs=1, type=str, help="The name of the\
        project. A directory with this name will be created.")
newParse.add_argument("--git-init", "-g", action="store_true", help="Initialise\
        git repository in project.")
newParse.set_defaults(func=_newOpt)

# Init
init = subparsers.add_parser("init", help="Initialise an Amor project.")
init.add_argument("project_name", nargs="?", type=str, help="The name of the\
                  project.")
init.add_argument("--force", '-f', action="store_true", help="Force the\
                  creation of a fresh amor.toml config file.")
init.add_argument("--git-init", '-g', action="store_true", help="Initialise\
        git repository in project.")
init.set_defaults(func=_initOpt)

# Install
install = subparsers.add_parser("install", aliases=["i", "add"], help="Install\
        the given module(s) to this project.")
install.add_argument('--force', '-f', action="store_true", help="Force the\
        force the re-installation of all modules.")
install.add_argument("module", nargs="*", type=str, help="Module(s) to install\
                     from Github. Given in format\
                     `<username>/<repository>[@<tag>]`. If <tag> is not present\
                     the most current version will be installed. If <tag> is\
                     present, but does not exist on repository, the most\
                     current version will be installed.")
install.set_defaults(func=_installOpt)

# Uninstall
uninstall = subparsers.add_parser('uninstall', aliases=['u', 'remove'], help="\
        Uninstall the given module(s) from the project.")
uninstall.add_argument('module', nargs="+", type=str, help="Module(s) to\
        uninstall, given in format `<module_name>` (as you would require\
        in a Lua script).")
uninstall.set_defaults(func=_uninstallOpt)

# Run
run = subparsers.add_parser("run", aliases=["r"], help="Run a script defined in\
        the project amor.toml config file.")
run.add_argument("script", nargs=1, type=str, help="Name of script to run.")
run.set_defaults(func=_runOpt)

# Build
build = subparsers.add_parser("build", aliases=["b"], help="Build project into\
        single directory for Löve.")
build.add_argument("--clean", "-c", action="store_true", help="Remove existing\
                   build folder contents.")
build.set_defaults(func=_buildOpt)

# Love
love = subparsers.add_parser("love", help="Run Löve using the current project's\
        build directory.")
love.set_defaults(func=_loveOpt)

args = parser.parse_args()
args.func(args)

