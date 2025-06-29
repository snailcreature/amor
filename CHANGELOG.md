# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
with versioning following the [Sem Ver 2.0.0](https://semver.org/spec/v2.0.0.html)
format.

`MAJOR.MINOR.PATCH`

1. `MAJOR` - Breaking changes
2. `MINOR` - Backward compatible additions
3. `PATCH` - Backward compatible bug fixes

***

## [0.2.2] - 2025-06-29

### Fixed

 - Build script now ignores `require`-ing of modules bundled with Love
 - Install script now creates an `init.lua` for installed modules that lack them
   even if they are not a compiled `*.so`

***

## [0.2.1] - 2025-06-28

### Fixed

 - Major bug in install script that skips built dependencies that do not have a
   build option (i.e. no rockspec)

***

## [0.2.0] - 2025-06-26

### Added

 - Calling `amor build --clean` will remove the existing build directory before
   beginning

### Fixed

 - Minor bug in `install.py` that meant built-on-install modules had the
   incorrect name
 - Major bug in `build.py` that would not copy included assets

***

## [0.1.2] - 2025-06-24

### Fixed

 - Major bug in `install.py` script that would attempt to double-copy a built module
 - Minor bugs in `setup` script where `[[-z` command could not be found

***

## [0.1.1] - 2025-06-21

### Added

 - Added copy source fallback if build-on-install fails
 - Added delete empty directories after copy source fallback

### Changed

 - Moved function definitions for different commands into separate Python files

***

## [0.1.0] - 2025-06-03

### Added

 -  Create new amor project
 -  Initialise amor in existing project
 -  Create or initialise project with git
 -  Build project, collecting all dependencies into single directory
 -  Install dependencies from GitHub
 -  Build dependencies automatically
 -  Track configuration and dependencies in `amor.toml`

 ***

