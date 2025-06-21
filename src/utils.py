# Utility functions

def getRepoTags(repo_url: str):
    """
    Get the tags of a remote repository.
    """
    from subprocess import PIPE, run as cmd
    res = cmd(["git", "ls-remote", "--tags", repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    tags = [
            line.split("refs/tags/")[-1] for line in out_lines
            if "refs/tags/" in line and "^{}" not in line
        ]
    return tags


def getRepoTagHashes(repo_url: str):
    """
    Get the hashes for the tagged releases of a remote repository.
    """
    from subprocess import PIPE, run as cmd
    res = cmd(["git", "ls-remote", "--tags", repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    tagHashes: dict[str, str] = {}
    
    for line in out_lines:
        if "refs/tags/" not in line or "^{}" in line:
            continue
        
        hash, tag = line.split('refs/tags/')
        tagHashes[tag] = hash.replace('\t', '')

    return tagHashes


def getRepoHeads(repo_url: str):
    """
    Get the HEAD commits of a remote repository.
    """
    from subprocess import PIPE, run as cmd
    res = cmd(['git', 'ls-remote', '--heads', repo_url], stdout=PIPE, text=True)

    out_lines = res.stdout.splitlines()

    for line in out_lines: print(line)

    heads = [
            line.split('refs/heads/')[0].replace('\t', '') for line in out_lines
            if "refs/heads/" in line and "^{}" not in line
            ]

    return heads


def getRepoHeadHash(repo_url: str):
    """
    Get the hash for the HEAD commit of a remote repository.
    """
    from subprocess import PIPE, run as cmd
    res = cmd(['git', 'ls-remote', repo_url, 'HEAD'], shell=False, stdout=PIPE,
            text=True)
     
    out_lines = res.stdout.splitlines()

    res.check_returncode()

    head = out_lines[0].split('HEAD')[0].replace('\t', '')

    return head


def include_patterns(*patterns):
    """
    Define the patterns to include in the tree when using shutil.copytree().
    """
    from fnmatch import filter as fil
    from os import path
    from typing import Any
    def _ignore_patterns(p: Any, names: list[str]):
        keep = set(name for pattern in patterns
                   for name in fil(names, pattern))

        ignore = set(name for name in names
                     if name not in keep and not path.isdir(path.join(p,
                                                                      name)))
        return ignore
    return _ignore_patterns


def remove_empty_dirs(dir):
    """
    Remove empty directories from a given base directory.
    """
    from os import walk, listdir
    from shutil import rmtree
    dirs = [x[0] for x in walk(dir)][1:]
    dirs.reverse()
    for sub_dir in dirs:
        if len(listdir(sub_dir)) == 0:
            try:
                rmtree(sub_dir)
                print(f"Removed {sub_dir}")
            except Exception as err:
                print(f"Could not delete {sub_dir} due to {err}.")
