from argparse import Namespace
from toml import load, dump
from shutil import rmtree

def uninstallOpt(args: Namespace):
    """
    Uninstall the given repositor(y/ies).
    """
    modules: list[str] = args.module

    with open('amor.toml', 'r') as amor_conf:
        conf = load(amor_conf)

    deps: dict[str, str] = conf["dependencies"]

    to_delete: list[str] = [dep for dep in deps if dep in modules]

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


