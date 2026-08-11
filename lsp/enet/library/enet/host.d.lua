---@meta

---Event sent to or from a host.
---
---@class enet.event
---@field type "connect" | "disconnect" | "receive" Type of event received
---@field peer enet.peer Peer object which triggered the event
---@field data string Packet data. Always a Lua string
enet.event = {}

---Flag to describe how a packet should be treated.
---
---@alias enet.flag
--- |"reliable" # Packets are guaranteed to arrive, and arrive in the order they were sent
--- |"unsequenced" # Unreliable and no guarantee on the order they arrive.
--- |"unreliable"

---A UDP host created by ENet.
---
---Can be bound to an address to create a server, or left unbound to create a
---client.
---
---@class enet.host
enet.host = {}

---Connects a host to a remove host. Returns peer object associated with remote
---host. The actual connection will not take place until the next `host:service`
---is done, in which a `"connect"` event will be generated.
---
---@param address string Address of the host
---@param channel_count integer? Number of channels to allocate. It should be the same as the channel count on the server. Defaults to 1.
---@param data integer? An integer value that can be associated with the connect event. Defaults to 0.
---@return enet.peer peer The connection to the server
function enet.host:connect(address, channel_count, data) end

---Wait for events, send and receive any ready packets.
---
---@param timeout integer? Max number of milliseconds to be waited for an event. By default is `0`
---@return enet.event|nil event Returns nil on timeout if no events occurred.
function enet.host:service(timeout) end

---Checks for any queued events and dispatches one if available
---
---@return enet.event|nil event Returns the associated event if something was dispatched, otherwise `nil`
function enet.host:check_events() end

---Enables the adaptive order-2 PPM range coder for the transmitted data of all
---peers.
function enet.host:compress_with_range_coder() end

---Sends any queued packets. This is only required to send packets earlier than
---the next call to [`host:service`](enet.host.service), or if `host:service` will not be called
---again.
function enet.host:flush() end

---Queues a packet to be send to all connected peers.
---
---@param data string Contents of the data packet, must be a Lua string.
---@param channel integer? Channel to send the packet on. Defaults to 0.
---@param flag enet.flag? Defaults to `"reliable"`
function enet.host:broadcast(data, channel, flag) end

---Sets the maximum number of channels allowed.
---
---@param limit integer Max number of allowed channels. If `0`, uses system maximum
function enet.host:channel_limit(limit) end

---Sets the bandwidth limits of the host in bytes/sec.
---
---@param incoming integer Downstream bandwidth in bytes/sec. Set to `0` for unlimited
---@param outgoing integer Upstream bandwidth in bytes/sec. Set to `0` for unlimited
function enet.host:bandwidth_limit(incoming, outgoing) end

---Returns the number of bytes that were sent through the given host.
---
---@return integer bytes Bytes sent through host
function enet.host:total_sent_data() end

---Returns the number of bytes that were received by the given host.
---
---@return integer bytes Bytes received by host
function enet.host:total_received_data() end

---Returns the timestamp of the last call to [`host:service()`](enet.host.service) or
---[`host:flush()`](enet.host.flush)
---
---@return string timestamp
function enet.host:service_time() end

---Returns the number of peers that were allocated for the given host. This
---represents the maximum number of possible connections.
---
---@return integer peers Number of allocated peers
function enet.host:peer_count() end

---Returns the connected peer at the specified index (starting at 1). ENet
---stores all peers in an array of the corresponding host and re-uses unused
---peers for new connections. You can query the state of a peer using [peer:state](enet.peer.state).
---
---@param index integer Peer index
---@return enet.peer peer
function enet.host:get_peer(index) end

---Returns a string that describes the socket address of the given host. The
---string is formatted as "a.b.c.d:port", where "a.b.c.d" is the ip address of
---the used socket.
---
---@return string socket_address
function enet.host:get_socket_address() end
