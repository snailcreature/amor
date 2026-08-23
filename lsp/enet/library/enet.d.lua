---@meta

---lua-enet is a binding to the ENet library for Lua. ENet is a thin network 
---communication layer over UDP that provides high performance and reliable communication 
---that is suitable for games. The interface exposes an asynchronous way of creating 
---clients and servers that is easy to integrate into existing event loops.
---
---[Open in browser](https://leafo.net/lua-enet/)
---
---@class enet
enet = {}

---Returns a new host. All arguments are optional.
---
---A `bind_address` of `nil` makes a host that can not be connected to
---(typically by a client). Otherwise the address can either be of the form
---`<ipaddress>:<port>`, `<hostname>:<port>`, or `*:<port>`.
---
---Example addresses include `"127.0.0.1:8888"`, `"localhost:2232"`, and `"*:6767"`.
---
---@param bind_address string? Address of server
---@param peer_count integer? Max number of peers, defaults to `64`
---@param channel_count integer ?Max number of channels, defaults to `1`
---@param in_bandwidth integer? Downstream bandwidth in bytes/sec, defaults to `0` (unlimited)
---@param out_bandwidth integer? Upstream bandwith in bytes/sec, defaults to `0` (unlimited)
---@return enet.host host
function enet.host_create(bind_address, peer_count, channel_count, in_bandwidth, out_bandwidth) end

return enet
