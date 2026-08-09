from typing import Literal, NamedTuple, TypedDict

type AmorVersion = Literal["0.5.0"] | Literal[None]

type AmorInstallMod = tuple[str, str, str | None]  # author, repo, tag

type AmorOldConfigDependency = tuple[str, str, str, str]  # author, repo, tag, hash


class AmorConfigDependency(TypedDict):
    src: str | None
    version: str | None


type AmorConfigDependencies = dict[str, AmorConfigDependency | str]


class AmorConfigProject(TypedDict):
    name: str
    version: str
    author: str | None
    description: str
    license: str | None
    love_version: str
    lua_version: Literal["5.4"] | Literal["5.3"] | Literal["5.2"] | Literal["5.1"]
    source_dir: str
    build_dir: str
    entry: str
    amor_version: AmorVersion


class AmorConfigBuild(TypedDict):
    include: list[str]


class AmorConfig(TypedDict):
    project: AmorConfigProject
    build: AmorConfigBuild
    scripts: dict[str, str]
    dependencies: dict[str, AmorConfigDependency | str]


class AmorLockEntry(TypedDict):
    src: str
    hash: str
    version: str | None
    author: str


type AmorLock = dict[str, AmorLockEntry]
