---@meta

---The url namespace provides functions to parse, protect, and build URLs, as well as functions to compose absolute URLs from base and relative URLs, according to RFC 2396.
---
---To obtain the url namespace, run:
---
---```lua
----- loads the URL module
---local url = require("socket.url")
---```
---
---An URL is defined by the following grammar:
---
---```
---    <url> ::= [<scheme>:][//<authority>][/<path>][;<params>][?<query>][#<fragment>]
---    <authority> ::= [<userinfo>@]<host>[:<port>]
---    <userinfo> ::= <user>[:<password>]
---    <path> ::= {<segment>/}<segment>
---```
---
---[See full documentation for examples](https://lunarmodules.github.io/luasocket/url.html)
---
---@class socket.url
socket.url = {}

---@class socket.url.ParsedUrl
---@field url string?
---@field scheme string?
---@field authority string?
---@field path string?
---@field params string?
---@field query string?
---@field fragment string?
---@field userinfo string?
---@field host string?
---@field port string?
---@field user string?
---@field password string?

---Builds an absolute URL from a base URL and a relative URL.
---
---Base is a string with the base URL or a parsed URL table. Relative is a
---string with the relative URL.
---
---The function returns a string with the absolute URL.
---
---Note: The rules that govern the composition are fairly complex, and are
---described in detail in RFC 2396.
---
---@param base string
---@param relative string
---@return string
function socket.url.absolute(base, relative) end

---Rebuilds an URL from its parts.
---
---Parsed_url is a table with same components returned by parse. Lower level
---components, if specified, take precedence over high level components of the
---URL grammar.
---
---The function returns a string with the built URL.
---
---@param parsed_url socket.url.ParsedUrl
---@return string
function socket.url.build(parsed_url) end

---Builds a <path> component from a list of <segment> parts. Before composition,
---any reserved characters found in a segment are escaped into their protected
---form, so that the resulting path is a valid URL path component.
---
---Segments is a list of strings with the <segment> parts. If unsafe is anything
---but nil, reserved characters are left untouched.
---
---The function returns a string with the built <path> component.
---
---@param segments string[]
---@param unsafe true|nil
---@return string
function socket.url.build_path(segments, unsafe) end

---Applies the URL escaping content coding to a string Each byte is encoded as
---a percent character followed by the two byte hexadecimal representation of
---its integer value.
---
---Content is the string to be encoded.
---
---The function returns the encoded string.
---
---@param content string
---@return string
function socket.url.escape(content) end

---Parses an URL given as a string into a Lua table with its components.
---
---Url is the URL to be parsed. If the default table is present, it is used to
---store the parsed fields. Only fields present in the URL are overwritten.
---Therefore, this table can be used to pass default values for each field.
---
---The function returns a table with all the URL components:
---
---```
---    parsed_url = {
---      url = string,
---      scheme = string,
---      authority = string,
---      path = string,
---      params = string,
---      query = string,
---      fragment = string,
---      userinfo = string,
---      host = string,
---      port = string,
---      user = string,
---      password = string
---    }
---```
---
---@param url string
---@param default socket.url.ParsedUrl?
---@return socket.url.ParsedUrl
function socket.url.parse(url, default) end

---Breaks a <path> URL component into all its <segment> parts.
---
---Path is a string with the path to be parsed.
---
---Since some characters are reserved in URLs, they must be escaped whenever
---present in a <path> component. Therefore, before returning a list with all
---the parsed segments, the function removes escaping from all of them.
---
---@param path string
---@return string[]
function socket.url.parse_path(path) end

---Removes the URL escaping content coding from a string.
---
---Content is the string to be decoded.
---
---The function returns the decoded string.
---
---@param content string
---@return string
function socket.url.unescape(content) end
