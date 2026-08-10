from typing import Literal, NamedTuple, Optional, TypedDict

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
    author: Optional[str]
    description: str
    license: Optional[str]
    love_version: Literal["11.5"]
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
    version: Optional[str]
    author: str


type AmorLock = dict[str, AmorLockEntry]
