# Default configuration
default_conf = {
            "project": {
                "name": "",
                "version": "0.0.1",
                "author": "",
                "description": "",
                "license": "",
                "love_version": "",
                "lua_version": "5.4",
                "source_dir": "src",
                "build_dir": "build",
                "entry": "main.lua",
                },
            "build": {
                "include": [
                    "*.png",
                    ],
                },
            "scripts": {
                "test": "echo \"Hello, World!\"",
                "build": "echo \"No build script defined!\"",
                },
            "dependencies": {},
            }

# Default .gitignore for projects
gitignore_lines = """\
/build
/dist
/.amor
""".splitlines(keepends=True)

# Default .gitattributes for projects
gitattributes_lines = """\
# Normalise line endings
* text=auto

# Enforce Unix line endings
* text eol=lf

# Treat these as binaries
*.png binary

""".splitlines(keepends=True)

# Basic Love2D entry file
main_lua_content = """\
function love.load(arg)
end

function love.update(dt)
end

function love.draw()
end
""".splitlines(keepends=True)

# Template for init.lua for C modules
init_lua_template_so = """\
local Path = (...):gsub("%p", "/")
local RequirePath = ...
local {mod} = package.loadlib("{mod}", Path.."/{mod}.so")
package.loaded["{mod}"] = {mod}
return {mod}
"""

init_lua_template_lua = """\
local RequirePath = ...
local mod = require "{mod}"
package.loaded["{mod}"] = mod
return mod
"""

love_builtins = [
        "enet",
        "socket",
        "utf8"
        ]
