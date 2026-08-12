---@meta

---Current state of an [`enet.peer`](enet.peer) instance.
---
---@alias enet.state
---| "disconnected"
---| "connecting"
---| "acknowledging_connect"
---| "connection_pending"
---| "connection_succeeded"
---| "connected"
---| "disconnect_later"
---| "disconnecting"
---| "acknowledging_disconnect"
---| "zombie"
---| "unknown"

---UDP peer for sending data and managing the connection to a server.
---
---@class enet.peer
enet.peer = {}

---Returns the field ENetPeer::connectID that is assigned for each connection.
---
---@return integer connect_id
function enet.peer:connect_id() end

---Requests a disconnection from the peer. The message is send on the next
---[`host:service`](enet.host.service) or [`host:flush`](enet.host.flush).
---
---@param data integer? Value to be associated with the disconnect
function enet.peer:disconnect(data) end

---Force immediate disconnection from peer. Foreign peer not guaranteed to
---receive disconnect notification.
---
---@param data integer? Value to be associated with the disconnect
function enet.peer:disconnect_now(data) end

---Request a disconnection from peer, but only after all queued outgoing
---packages are sent.
---
---@param data integer? Value to be associated with the disconnect
function enet.peer:disconnect_later(data) end

---Returns the index of the peer. All peers of an ENet host are kept in an
---array. This function finds and returns the index of the peer of its host
---structure.
---
---@return integer index
function enet.peer:index() end

---Send a ping request to peer, updates `round_trip_time`. This is called
---automatically at regular intervals.
---
function enet.peer:ping() end

---Specifies the interval in milliseconds that pings are sent to the other end
---of the connection (defaults to 500).
---
---@param interval integer Interval in milliseconds
function enet.peer:ping_interval(interval) end

---Forcefully disconnects peer. The peer is not notified of the disconnection.
---
function enet.peer:reset() end

---Queues a packet to be send to peer.
---
---@param data string Contents of the packet, it must be a Lua string
---@param channel integer? Channel to send the packet on. Defaults to `0`
---@param flag enet.flag? Defaults to `"reliable"`
function enet.peer:send(data, channel, flag) end

---Returns the state of the peer as a string.
---
---@return enet.state state
function enet.peer:state() end

---Attempts to dequeue an incoming packet for this peer.
---
---@return [string, integer]|nil packet Returns `nil` if there are no packets
---waiting. Otherwise returns two values: the string representing the packet
---data, and the channel the packet came from
function enet.peer:receive() end

---Returns the current round trip time (i.e. ping).
---
---Enet performs some filtering on the round trip times and it takes some time
---until the parameters are accurate.
---
---@return integer roundTripTime Current round trip time
function enet.peer:round_trip_time() end

---Sets the current round trip time(i.e. ping).
---
---@param value integer Value to set roundTripTime to
---@return integer roundTripTime Value roundTripTime was just set to
function enet.peer:round_trip_time(value) end

---Sets the round trip time of the previous round trip time computation.
---
---Enet performs some filtering on the round trip times and it takes some time 
---until the parameters are accurate. To speed it up you can set the value of the 
---last round trip time to a more accurate guess.
---
---@return integer lastRoundTripTime Current round trip time
function enet.peer:last_round_trip_time() end

---Sets the round trip time of the previous round trip time computation.
---
---@param value integer Value to set lastRoundTripTime to
---@return integer lastRoundTripTime Value lastRoundTripTime was just set to
function enet.peer:last_round_trip_time(value) end

---Changes the probability at which unreliable packets should not be dropped.
---
---@param interval integer Milliseconds to measure lowest mean RTT
---@param acceleration number Rate at which to increase throttle probability as mean RTT declines
---@param deceleration number Rate at which to decrease throttle probability as mean RTT increases
function enet.peer:throttle_configure(interval, acceleration, deceleration) end

---Returns or sets the parameters when a timeout is detected. This happens
---either after a fixed timeout or a variable timeout of time that takes the
---round trip into account. The former is specified when the `maximum` parameter.
---
---See official ENet documentation for detailed description.
---
---@param limit number Factor that is multiplied with a value that based on the average round trip time to compute the timeout limit
---@param minimum integer Minimum timeout value in milliseconds
---@param maximum integer Maximum timeout value in milliseconds
function enet.peer:timeout(limit, minimum, maximum) end
