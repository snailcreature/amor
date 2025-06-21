from argparse import Namespace

def loveOpt(_args: Namespace):
    """
    Run Löve2D on the project build directory.
    """
    from toml import load
    from os import getcwd, environ
    from subprocess import PIPE, run as cmd
    
    with open('amor.toml', 'r') as conf:
        amor_conf = load(conf)

    build_dir = amor_conf["project"]["build_dir"]
    cwd = getcwd()
    lua_env = environ.copy()
    lua_env["LUA_PATH"] = f"?;?.lua;{cwd}/{build_dir}/?/init.lua;{cwd}/{build_dir}/?.lua;\
            {lua_env['LUA_PATH']}"
    lua_env["LUA_CPATH"] = f"?;?.so;{cwd}/{build_dir}/?.so;{cwd}/{build_dir}/?/?.so;{lua_env['LUA_CPATH']}"
        
    res = cmd(["love", build_dir], stdout=PIPE, text=True, env=lua_env)

    for line in res.stdout.splitlines(): print(line)
    
    res.check_returncode()
    return
 
