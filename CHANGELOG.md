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

## [UNRELEASED]

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

