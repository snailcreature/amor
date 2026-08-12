---@meta

---@class socket.dns
socket.dns = {}

---@class socket.dns.resolved4
---@field name string Canonic name
---@field alias string[] List of aliases; can be empty
---@field ip string[] List of IP addresses
socket.dns.resolved4 = {}

---@class socket.dns._resolved6_entry
---@field family "inet"|"inet6"
---@field addr string
socket.dns._resolved6_entry = {}

---@class socket.dns.resolved6
---@field [number] socket.dns._resolved6_entry

---Converts from host name to address.
---
---Address can be an IPv4 or IPv6 address or host name.
---
---The function returns a table with all information returned by the resolver. In
---case of error, the function returns nil followed by an error message. 
---
---@param address string IPv4 or IPv6 address or host name
---@return [socket.dns.resolved6, nil]|[nil, string]
function socket.dns.getaddrinfo(address) end

---Returns the standard host name for the machine as a string.
---
---@return string
function socket.dns.gethostname() end

---Converts from IPv4 address to host name.
---
---Address can be an IP address or host name.
---
---The function returns a string with the canonic host name of the given address,
---followed by a table with all information returned by the resolver. In case of
---error, the function returns nil followed by an error message.
---
---@param address string IP address or host name
---@return [string, socket.dns.resolved4]|[nil, string]
function socket.dns.tohostname(address) end

---Converts from host name to IPv4 address.
---
---Address can be an IP address or host name.
---
---Returns a string with the first IP address found for address, followed by a table
---with all information returned by the resolver. In case of error, the function
---returns nil followed by an error message. 
---
---@param address string IP address or host name
---@return [string, socket.dns.resolved4]|[nil, string]
function socket.dns.toip(address) end
