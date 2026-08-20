---@meta

---Core functionality of LuaSocket
---
---[Open in browser](https://lunarmodules.github.io/luasocket/)
---
---@class socket
---@field _DEBUG boolean This constant is set to `true` if the library was compiled with debug support.
---@field _DATAGRAMSIZE integer Default datagram size used by calls to receive and receivefrom. (Unless changed in compile time, the value is 8192.)
---@field _SETSIZE integer Maximum number of sockets that the select function can handle
---@field _SOCKETINVALID unknown The OS value for an invalid socket. This can be used with `tcp:getfd` and `tcp:setfd` methods.
---@field _VERSION string This constant has a string describing the current LuaSocket version.
socket = {}

socket.headers = {}

---@type headers
socket.headers.canonic = headers

---@class socket.Ok<O>
---@field [1] O
---@field [2] nil

---@class socket.Err<E>
---@field [1] nil
---@field [2] E

---@generic O
---@generic E
---@alias socket.Result
--- | socket.Ok<O>
--- | socket.Err<E>

--- This function is a shortcut that creates and returns a TCP server object bound
--- to a local address and port, ready to accept client connections. Optionally,
--- user can also specify the backlog argument to the listen method (defaults to
--- 32).
---
--- Note: The server object returned will have the option "reuseaddr" set to true.
---@param address string Local address of the server
---@param port integer Local port of the server
---@param backlog integer? Number of client connections that can be queues waiting for service
---@return socket.server
function socket.bind(address, port, backlog) end

---This function is a shortcut that creates and returns a TCP client object connected
---to a remote address at a given port. Optionally, the user can also specify the
---local address and port to bind (locaddr and locport), or restrict the socket
---family to "inet" or "inet6". Without specifying family to connect, whether a
---tcp or tcp6 connection is created depends on your system configuration. Two
---variations of connect are defined as simple helper functions that restrict the
---family, socket.connect4 and socket.connect6.
---
---@param address string
---@param port integer
---@param locaddr string
---@param locport integer
---@param family "inet"|"inet6"
---@return socket.client
function socket.connect(address, port, locaddr, locport, family) end

---This function is a shortcut that creates and returns a TCP client object connected
---to a remote address at a given port. Optionally, the user can also specify the
---local address and port to bind (locaddr and locport), or restrict the socket
---family to "inet" or "inet6". Without specifying family to connect, whether a
---tcp or tcp6 connection is created depends on your system configuration. Two
---variations of connect are defined as simple helper functions that restrict the
---family, socket.connect4 and socket.connect6.
---
---@param address string
---@param port integer
---@param locaddr string
---@param locport integer
---@param family "inet"
---@return socket.client
function socket.connect4(address, port, locaddr, locport, family) end

---This function is a shortcut that creates and returns a TCP client object connected
---to a remote address at a given port. Optionally, the user can also specify the
---local address and port to bind (locaddr and locport), or restrict the socket
---family to "inet" or "inet6". Without specifying family to connect, whether a
---tcp or tcp6 connection is created depends on your system configuration. Two
---variations of connect are defined as simple helper functions that restrict the
---family, socket.connect4 and socket.connect6.
---
---@param address string
---@param port integer
---@param locaddr string
---@param locport integer
---@param family "inet6"
---@return socket.client
function socket.connect6(address, port, locaddr, locport, family) end

---Returns the UNIX time in seconds. You should subtract the values returned by
---this function to get meaningful values.
---
---```lua
---t = socket.gettime()
----- do stuff
---print(socket.gettime() - t .. " seconds elapsed")
---```
---
---@return number
function socket.gettime() end

---Creates and returns a clean try function that allows for cleanup before the
---exception is raised. This implements the ideas described in LTN012, Using finalized
---exceptions.
---
---Finalizer is a function that will be called before try throws the exception.
---
---The function returns your customized try function.
---
---Note: This idea saved a lot of work with the implementation of protocols in LuaSocket:
---
---```lua
---foo = socket.protect(function()
---    -- connect somewhere
---    local c = socket.try(socket.connect("somewhere", 42))
---    -- create a try function that closes 'c' on error
---    local try = socket.newtry(function() c:close() end)
---    -- do everything reassured c will be closed
---    try(c:send("hello there?\r\n"))
---    local answer = try(c:receive())
---    ...
---    try(c:send("good bye\r\n"))
---    c:close()
---end)
---```
---@generic T: function
---@param finalizer T
---@return T
function socket.newtry(finalizer) end

---Converts a function that throws exceptions into a safe function. This function
---only catches exceptions thrown by the try and newtry functions. It does not
---catch normal Lua errors. This implements the ideas described in [LTN012, Using
---finalized exceptions](https://github.com/lunarmodules/luasocket/blob/master/ltn013.md).
---
---Func is a function that calls try (or assert, or error) to throw exceptions.
---
---Returns an equivalent function that instead of throwing exceptions in case of
---a failed try call, returns nil followed by an error message.
---
---@generic T: function
---@param func T
---@return T
function socket.protect(func) end

---Waits for a number of sockets to change status.
---
---Recvt is an array with the sockets to test for characters available for reading.
---Sockets in the sendt array are watched to see if it is OK to immediately write
---on them. Timeout is the maximum amount of time (in seconds) to wait for a change
---in status. A nil, negative or omitted timeout value allows the function to block
---indefinitely. Recvt and sendt can also be empty tables or nil. Non-socket values
---(or values with non-numeric indices) in the arrays will be silently ignored.
---
---The function returns a list with the sockets ready for reading, a list with
---the sockets ready for writing and an error message. The error message is "timeout"
---if a timeout condition was met, "select failed" if the call to select failed,
---and nil otherwise. The returned tables are doubly keyed both by integers and
---also by the sockets themselves, to simplify the test if a specific socket has
---changed status.
---
---**Note:** select can monitor a limited number of sockets, as defined by the
---constant socket._SETSIZE. This number may be as high as 1024 or as low as 64
---by default, depending on the system. It is usually possible to change this at
---compile time. Invoking select with a larger number of sockets will raise an error.
---
---**Important note:** a known bug in WinSock causes select to fail on non-blocking
---TCP sockets. The function may return a socket as writable even though the socket
---is not ready for sending.
---
---**Another important note:** calling select with a server socket in the receive
---parameter before a call to accept does not guarantee accept will return immediately.
---Use the settimeout method or accept might block forever.
---
---**Yet another note:** If you close a socket and pass it to select, it will be
---ignored.
---
---**Using select with non-socket objects:** Any object that implements getfd and
---dirty can be used with select, allowing objects from other libraries to be used
---within a socket.select driven loop.
---
---@param recvt integer[]
---@param sendt integer[]
---@param timeout number?
---@return [integer[], integer[], "timeout"|"select failed"|nil]
function socket.select(recvt, sendt, timeout) end

--- Creates an LTN12 sink from a stream socket object.
---
--- Mode defines the behavior of the sink. The following options are available:
---
--- "http-chunked": sends data through socket after applying the chunked transfer coding, closing the socket when done;
--- "close-when-done": sends all received data through the socket, closing the socket when done;
--- "keep-open": sends all received data through the socket, leaving it open when done.
---
---Socket is the stream socket object used to send the data.
---
---The function returns a sink with the appropriate behavior.
---
---@param mode # Behaviour of the sink
--- | "http-chunked" # sends data through socket after applying the chunked transfer coding, closing the socket when done
--- | "close-when-done" # sends all received data through the socket, closing the socket when done
--- | "keep-open" # sends all received data through the socket, leaving it open when done
---@param socket socket.socket
---@return ltn12.sink.sink
function socket.sink(mode, socket) end

---Drops a number of arguments and returns the remaining.
---
---D is the number of arguments to drop. Ret1 to retN are the arguments.
---
---The function returns retd+1 to retN.
---
---Note: This function is useful to avoid creation of dummy variables:
---
---```lua
----- get the status code and separator from SMTP server reply
---local code, sep = socket.skip(2, string.find(line, "^(%d%d%d)(.?)"))
---
---
---@generic T: unknown
---@param d integer
---@param ... T
---@return T ...
function socket.skip(d, ...) end

---Freezes the program execution during a given amount of time.
---
---Time is the number of seconds to sleep for. If time is negative, the function
---returns immediately.
---
---@param time number
function socket.sleep(time) end

---Creates an LTN12 source from a stream socket object.
---
---Mode defines the behavior of the source. The following options are available:
--- "http-chunked": receives data from socket and removes the chunked transfer coding before returning the data;
--- "by-length": receives a fixed number of bytes from the socket. This mode requires the extra argument length;
--- "until-closed": receives data from a socket until the other side closes the connection.
---
---Socket is the stream socket object used to receive the data.
---
---The function returns a source with the appropriate behavior.
---
---@param mode # the behavior of the source
--- | "http-chunked" # receives data from socket and removes the chunked transfer coding before returning the data
--- | "by-length" # receives a fixed number of bytes from the socket. This mode requires the extra argument length
--- | "until-closed" # receives data from a socket until the other side closes the connection
---@param socket socket.socket
---@param length integer?
---@return ltn12.source.source
function socket.source(mode, socket, length) end

---Throws an exception in case ret1 is falsy, using ret2 as the error message.
---The exception is supposed to be caught by a protected function only. This
---implements the ideas described in LTN012, Using finalized exceptions.
---
---Ret1 to retN can be arbitrary arguments, but are usually the return values
---of a function call nested with try.
---
---The function returns ret1 to retN if ret1 is not nil or false. Otherwise, it
---calls error passing ret2 wrapped in a table with metatable used by protect to
---distinguish exceptions from runtime errors.
---
---```lua
---connects or throws an exception with the appropriate error message
---c = socket.try(socket.connect("localhost", 80))
---```
---
---@param ret1 any
---@param ... unknown
---@return table|unknown ...
function socket.try(ret1, ...) end

---Creates and returns an TCP master object. A master object can be transformed
---into a server object with the method listen (after a call to bind) or into a
---client object with the method connect. The only other method supported by a
---master object is the close method.
---
---In case of success, a new master object is returned. In case of error, nil
---is returned, followed by an error message.
---
---Note: The choice between IPv4 and IPv6 happens during a call to bind or
---connect, depending on the address family obtained from the resolver.
---
---Note: Before the choice between IPv4 and IPv6 happens, the internal socket
---object is invalid and therefore setoption will fail.
---
---@return socket.Result<socket.master, string>
function socket.tcp() end

---Creates and returns an IPv4 TCP master object. A master object can be
---transformed into a server object with the method listen (after a call to
---bind) or into a client object with the method connect. The only other
---method supported by a master object is the close method.
---
---In case of success, a new master object is returned. In case of error, nil
---is returned, followed by an error message.
---
---@return socket.Result<socket.master, string>
function socket.tcp4() end

---Creates and returns an IPv6 TCP master object. A master object can be
---transformed into a server object with the method listen (after a call to
---bind) or into a client object with the method connect. The only other method
---supported by a master object is the close method.
---
---In case of success, a new master object is returned. In case of error, nil
---is returned, followed by an error message.
---
---Note: The TCP object returned will have the option "ipv6-v6only" set to true.
---
---@return socket.Result<socket.master, string>
function socket.tcp6() end

---@class MCS_Common
local mcs_common = {}

---Closes a TCP object. The internal socket used by the object is closed and the
---local address to which the object was bound is made available to other
---applications. No further operations (except for further calls to the `close`
---method) are allowed on a closed socket.
---
---Note: It is important to close all used sockets once they are not needed,
---since, in many systems, each socket uses a file descriptor, which are limited
---system resources. Garbage-collected objects are automatically closed before
---destruction, though.
---
function mcs_common:close() end

---Check the read buffer status.
---
---Returns `true` if there is any data in the read buffer, `false` otherwise.
---
---Note: *This is an internal method, use at your own risk.*
---
---@return boolean
function mcs_common:dirty() end

---Returns the underling socket descriptor or handle associated to the object.
---
---The descriptor or handle. In case the object has been closed, the return
---value will be `-1`. For an invalid socket it will be [_SOCKETINVALID].
---
---Note: *This is an internal method. Unlikely to be portable. Use at your own
---risk.*
---
---@return number
function mcs_common:getfd() end

---Returns the local address information associated to the object.
---
---Returns a string with the IP address of the peer, the port number that peer
---is using for the connection and a string with the family (`"inet"` or
---`"inet6"`). In case of error, the method returns `nil`.
---
---@return [string, integer, 'inet'|'inet6']|nil ...
function mcs_common:getsockname() end

---Returns accounting information on the socket, useful for throttling of
---bandwidth.
---
---The method returns the number of bytes received, the number of bytes sent,
---and the age of the socket object in seconds.
---
---@return [integer, integer, number] ...
function mcs_common:getstats() end

---Returns the current block timeout followed by the current total timeout.
---
---@return [number, number] ...
function mcs_common:gettimeout() end

---Resets accounting information on the socket, useful for throttling of
---bandwidth.
---
---`Received` is a number with the new number of bytes received. `Sent` is a
---number with the new number of bytes sent. `Age` is the new age in seconds.
---
---The method returns 1 in case of success and nil otherwise.
---
---@param received integer
---@param send integer
---@param age number
---@return 1|nil
function mcs_common:setstats(received, send, age) end

---Changes the timeout values for the object. By default, all I/O operations
---are blocking. That is, any call to the methods [send], [receive], and [accept]
---will block indefinitely, until the operation completes. The settimeout
---method defines a limit on the amount of time the I/O methods can block.
---When a timeout is set and the specified amount of time has elapsed,
---the affected methods give up and fail with an error code.
---
---The amount of time to wait is specified as the value parameter, in seconds.
---There are two timeout modes and both can be used together for fine tuning:
---
---* 'b': block timeout. Specifies the upper limit on the amount of time
--- LuaSocket can be blocked by the operating system while waiting for
--- completion of any single I/O operation. This is the default mode;
---* 't': total timeout. Specifies the upper limit on the amount of time
--- LuaSocket can block a Lua script before returning from a call.
---
---The nil timeout value allows operations to block indefinitely. Negative
---timeout values have the same effect.
---
---Note: although timeout values have millisecond precision in LuaSocket,
---large blocks can cause I/O functions not to respect timeout values due to
---the time the library takes to transfer blocks to and from the OS and to and
---from the Lua interpreter. Also, function that accept host names and perform
---automatic name resolution might be blocked by the resolver for longer than
---the specified timeout value.
---
---Note: The old timeout method is deprecated. The name has been changed for
---sake of uniformity, since all other method names already contained verbs
---making their imperative nature obvious.
---
---@param value number|nil
---@param mode ('b'|'t')?
function mcs_common:settimeout(value, mode) end

---Sets the underling socket descriptor or handle associated to the object.
---The current one is simply replaced, not closed, and no other change to the
---object state is made. To set it as invalid use _SOCKETINVALID.
---
---No return value.
---
---Note: *This is an internal method. Unlikely to be portable. Use at your own
---risk.*
---
---@param fd number
function mcs_common:setfd(fd) end

---@class socket.master: MCS_Common
master = mcs_common

---Binds a master object to `address` and `port` on local host.
---
---`Address` can be an IP address or a host name. `Port` must be an integer
---number in the range [0..64K]. If `address` is `'*'`, the system binds to all
---local interfaces using the `INADDR_ANY` constant or `IN6ADDR_ANY_INIT`,
---accoring to the family. If `port` is `0`, the system automatically chooses an
---ephemeral port.
---
---In case of success, the method return `1`. In case of error, the method
---returns `nil` followed by an error message.
---
---Note: The function [`socket.bind`](lua://socket.bind) is available and is a
---shortcut for the creation of server sockets.
---
---@param address string
---@param port integer
---@return socket.Result<1, string> ...
function master:bind(address, port) end

---Attempts to connect a master object to a remote host, transforming it into a
---client object. Client objects support methods [send], [receive],
---[getsockname], [getpeername], [settimeout], and [close].
---
---`Address` can be an IP address or a host name. `Port` must be an integer
---number in the range [1..64K].
---
---In case of error, the method returns `nil` followed by a string describing
---the error. In case of success, the method returns 1.
---
---Node: The function [socket.connect](lua://socket.connect) is available and is
---a shortcut for the creation of client sockets.
---
---Note: Starting with LuaSocket 2.0, the [settimeout] method affects the
---behaviour of `connect`, causing it to return with an error in case of a
---timeout. If that happens, you can still call
---[socket.select](lua://socket.select) with the socket in the `sendt` table.
---The socket will be writable when the connection is established.
---
---Note: Starung with LuaSocket 3.0, the host name resolution depends on whether
---the socket was created by [socket.tcp](lua://socket.tcp),
---[socket.tcp4](lua://socket.tcp4) or [socket.tcp6](lua://socket.tcp6).
---Addresses from the appropriate family (or both) are tried in the order
---returned by the resolver until the first success or until the last failure.
---If the timeout was set to zero, only the first address is tried.
---
---@param address string
---@param port integer
---@return socket.Result<1, string> ...
function master:connect(address, port) end

---Specofoes the socket is willing to receive connections, transforming the
---object into a server object. Server objects support the [accept],
---[getsockname], [setoption], [settimeout], and [close] methods.
---
---The parameter `backlog` specifies the number of client connections that can
---be queued waiting for service. If the queue is full and another client
---attempts connection, the connection is refused.
---
---In case of success, the method returns 1. In case of error, the method
---returns `nil` followed by an error message.
---
---@param backlog integer
---@return socket.Result<1, string>
function master:listen(backlog) end

---@class SC_Common: MCS_Common
local sc_common = mcs_common

---Gets the options for the TCP object. See [setoption] for description of the
---option names and values.
---
---`Option` is a string with the option name.
---
---The method returns the option value in case of success, or `nil` followed by
---an error message otherwise
---@param option unknown
---@return socket.Result<unknown, string> ...
---@overload fun(self, option: 'keepalive'): socket.Result<boolean, string>
---@overload fun(self, option: 'linger'): socket.Result<{on: boolean, timeout: integer}, string>
---@overload fun(self, option: 'reuseaddr'): socket.Result<boolean, string>
---@overload fun(self, option: 'tcp-nodelay'): socket.Result<boolean, string>
---@overload fun(self, option: 'tcp-keepidle'): socket.Result<number, string>
---@overload fun(self, option: 'tcp-keepcnt'): socket.Result<number, string>
---@overload fun(self, option: 'tcp-keepintvl'): socket.Result<number, string>
---@overload fun(self, option: 'tcp-defer-accept'): socket.Result<integer, string>
---@overload fun(self, option: 'tcp-fastopen'): socket.Result<integer, string>
---@overload fun(self, option: 'tcp-fastopen-connect'): socket.Result<boolean, string>
---@overload fun(self, option: 'ipv6-v6only'): socket.Result<boolean, string>
function sc_common:getoption(option) end

---Sets options for the TCP object. Options are only needed by low-level or
---time-critical applications. You should only modify an option if you are sure
---you need it.
---
---Option is a string with the option name, and value depends on the option
---being set:
---
---* 'keepalive': Setting this option to true enables the periodic transmission
--- of messages on a connected socket. Should the connected party fail to
--- respond to these messages, the connection is considered broken and
--- processes using the socket are notified;
---* 'linger': Controls the action taken when unsent data are queued on a
--- socket and a close is performed. The value is a table with a boolean entry
--- 'on' and a numeric entry for the time interval 'timeout' in seconds. If the
--- 'on' field is set to true, the system will block the process on the close
--- attempt until it is able to transmit the data or until 'timeout' has passed.
--- If 'on' is false and a close is issued, the system will process the close
--- in a manner that allows the process to continue as quickly as possible.
--- I do not advise you to set this to anything other than zero;
---* 'reuseaddr': Setting this option indicates that the rules used in
--- validating addresses supplied in a call to bind should allow reuse of
--- local addresses;
---* 'tcp-nodelay': Setting this option to true disables the Nagle's algorithm
--- for the connection;
---* 'tcp-keepidle': value in seconds for TCP_KEEPIDLE Linux only!!
---* 'tcp-keepcnt': value for TCP_KEEPCNT Linux only!!
---* 'tcp-keepintvl': value for TCP_KEEPINTVL Linux only!!
---* 'tcp-defer-accept': value for TCP_DEFER_ACCEPT Linux only!!
---* 'tcp-fastopen': value for TCP_FASTOPEN Linux only!!
---* 'tcp-fastopen-connect': value for TCP_FASTOPEN_CONNECT Linux only!!
---* 'ipv6-v6only': Setting this option to true restricts an inet6 socket to
--- sending and receiving only IPv6 packets.
---
---The method returns 1 in case of success, or nil followed by an error
---message otherwise.
---
---Note: The descriptions above come from the man pages.
---
---@param option unknown
---@param value unknown?
---@return socket.Result<1, string> ...
---@overload fun(self, option: 'keepalive', value: boolean?): socket.Result<1, string>
---@overload fun(self, option: 'linger', value: {on: boolean, timeout: integer}?): socket.Result<1, string>
---@overload fun(self, option: 'reuseaddr', value: boolean?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-nodelay', value: boolean?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-keepidle', value: number?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-keepcnt', value: number?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-keepintvl', value: number?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-defer-accept', value: integer?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-fastopen', value: integer?): socket.Result<1, string>
---@overload fun(self, option: 'tcp-fastopen-connect', value: boolean?): socket.Result<1, string>
---@overload fun(self, option: 'ipv6-v6only', value: boolean?): socket.Result<1, string>
function sc_common:setoption(option, value) end

---@class socket.server: SC_Common
server = sc_common

---Waits for a remote connection on the server object and returns a client
---object representing that connection.
---
---If a connection is successfully initiated, a client object is returned. If a
---timeout condition is met, the method returns `nil` followed by the error
---string `'timeout'`. Other errors are reported by `nil` followed by a message
---describing the error.
---
---Note: calling [`socket.select`](lua://socket.select) with a server object in `recvt`
---parameter before a call to `accept` does *not* guarantee `accept` will return
---immediately. Use the [`settimeout`] method or `accept`
---might block until *another* client shows up.
---
---@return socket.Result<socket.client, 'timeout'|string> ...
function server:accept() end

---@class socket.client: SC_Common
client = sc_common

---Returns information about the remote side of a connected client object.
---
---Returns a string with the IP address of the peer, the port number that peer
---is using for the connection and a string with the family (`"inet"` or
---`"inet6"`). In case of error, the method returns `nil`.
---
---Note: It makes no sense to call this method on server objects.
---
---@return [string, integer, 'inet'|'inet6']|nil ...
function client:getpeername() end

---Reads data from a client object, according to the specified read pattern.
---Patterns follow the Lua file I/O format, and the difference in performance
---between all patterns is negligible.
---
---`Pattern` can be any of the following:
---
---* `'*a'`: reads from the socket until the connection is closed. No
--- end-of-line translation is performed;
---* `'*l'`: reads a line of text from the socket. The line is terminated by a
--- LF character (ASCII 10), optionally preceded by a CR character (ASCII 13).
--- The CR and LF characters are not included in the returned line. In fact,
--- *all* CR characters are ignored by the pattern. This is the default pattern;
---* `number`: causes the method to read a specified number of bytes from the socket.
---
---`Prefix` is an optional string to be concatenated to the beginning of any
---received data before return.
---
---If successful, the method returns the received pattern. In case of error,
---the method returns nil followed by an error message, followed by a (possibly
---empty) string containing the partial that was received. The error message
---can be the string 'closed' in case the connection was closed before the
---transmission was completed or the string 'timeout' in case there was a
---timeout during the operation.
---
---*Important Note:* This function was changed *severely*. It used to support
---multiple patterns (but I have never seen this feature used) and now it
---doesn't anymore. Partial results used to be returned in the same way as
---successful results. This last feature violated the idea that all functions
---should return `nil` on error. This it was changed too.
---
---@param pattern? '*a'|'*l'|number
---@param prefix string?
---@return socket.Result<string, [string|'closed'|'timeout', string]>
function client:receive(pattern, prefix) end

---Sends data through client object.
---
---Data is the string to be sent. The optional arguments i and j work exactly
---like the standard string.sub Lua function to allow the selection of a
---substring to be sent.
---
---If successful, the method returns the index of the last byte within [i, j]
---that has been sent. Notice that, if i is 1 or absent, this is effectively
---the total number of bytes sent. In case of error, the method returns nil,
---followed by an error message, followed by the index of the last byte within
---[i, j] that has been sent. You might want to try again from the byte
---following that. The error message can be 'closed' in case the connection was
---closed before the transmission was completed or the string 'timeout' in case
---there was a timeout during the operation.
---
---Note: Output is not buffered. For small strings, it is always better to
---concatenate them in Lua (with the '..' operator) and send the result in one
---call instead of calling the method several times.
---
---@param data string
---@param i integer?
---@param j integer?
function client:send(data, i, j) end

---Shuts down part of a full-duplex connection.
---
---Mode tells which way of the connection should be shut down and can take
---the value:
---
---* "both": disallow further sends and receives on the object. This is the
--- default mode;
---* "send": disallow further sends on the object;
---* "receive": disallow further receives on the object.
---
---This function returns 1.
---
---@param mode 'both'|'send'|'receive'
---@return 1
function client:shutdown(mode) end

---@class udp_common
local udp_common = {}

---Closes a UDP object. The internal socket used by the object is closed and the
---local address to which the object was bound is made available to other
---applications. No further operations (except further calls to the `close`
---method) are allowed on a closed docket.
---
---Note: It is important to close all used sockets once they are not needed,
---since, in many systems, each socket uses a file descriptor, which a re
---limited system resources. Garbage-collected objects are automatically closed
---before destruction, though.
---
function udp_common:close() end

---@class socket.UDP_Membership
---@field multiaddr string IP Address
---@field interface string IP Address

---Gets an option value from the UDP object. See setoption for description of
---the option names and values.
---
---Option is a string with the option name.
---
---The method returns the option value in case of success, or nil followed by
---an error message otherwise.
---
---@param option unknown
---@return socket.Result<unknown, string>
---@overload fun(self, option: 'dontroute'|'broadcast'|'reuseaddr'|'reuseport'|'ip-multicast-loop'|'ipv6-v6only'): socket.Result<boolean, string>
---@overload fun(self, option: 'ip-multicast-if'): socket.Result<string, string>
---@overload fun(self, option: 'ip-multicast-ttl'): socket.Result<integer, string>
---@overload fun(self, option: 'ip-add-membership'): socket.Result<socket.UDP_Membership, string>
---@overload fun(self, option: 'ip-drop-membership'): socket.Result<socket.UDP_Membership, string>
function udp_common:getoption(option) end

---Returns the local address information associated to the object.
---
---Returns a string with the IP address of the peer, a number with the local port,
---and a string with the family. In case of error, the method returns nil.
---
---Note: UDP sockets are not bound to any address until the [setsockname] or the
---[sendto] method is called for the first time (in which case it is bound to an
---ephemeral port and the wild-card address).
---
---@return [string, integer, "inet"|"inet6"]|nil ...
function udp_common:getsockname() end

---Returns the current timeout value.
---
---@return number
function udp_common:gettimeout() end

---Receives a datagram from the UDP object. If the UDP object is connected, only
---datagrams coming from the peer are accepted. Otherwise, the returned datagram
---can come from any host.
---
---The optional `size` parameter specifies the maximum size of the datagram to be
---retrieved. If there are more than `size` bytes available in the datagram, the
---excess bytes are discarded. If there are less than `size` bytes available in
---the current datagram, the available bytes are returned. If `size` is omitted,
---the compile-time constant [socket._DATAGRAMSIZE] is used (it defaults to 8192
---bytes). Larger sizes will cause a temporary buffer to be allocated for the operation.
---
---In case of success the method returns the received datagram, In case of
---timeout, the method returns nil followed by the string `'timeout'`.
---
---@param size integer?
---@return socket.Result<string, "timeout">
function udp_common:receive(size) end

---Sets options for the UDP object. Options are only needed by low-level or
---time-critical applications. You should only modify an option if you are
---sure you need it.
---
---Option is a string with the option name, and value depends on the option
---being set:
---
--- 'dontroute': Indicates that outgoing messages should bypass the standard
---     routing facilities. Receives a boolean value;
--- 'broadcast': Requests permission to send broadcast datagrams on the socket.
---     Receives a boolean value;
--- 'reuseaddr': Indicates that the rules used in validating addresses supplied
---     in a bind() call should allow reuse of local addresses. Receives a
---     boolean value;
--- 'reuseport': Allows completely duplicate bindings by multiple processes if
---     they all set 'reuseport' before binding the port. Receives a boolean value;
--- 'ip-multicast-loop': Specifies whether or not a copy of an outgoing
---     multicast datagram is delivered to the sending host as long as it is a
---     member of the multicast group. Receives a boolean value;
--- 'ipv6-v6only': Specifies whether to restrict inet6 sockets to sending and
---     receiving only IPv6 packets. Receive a boolean value;
--- 'ip-multicast-if': Sets the interface over which outgoing multicast
---     datagrams are sent. Receives an IP address;
--- 'ip-multicast-ttl': Sets the Time To Live in the IP header for outgoing
---     multicast datagrams. Receives a number;
--- 'ip-add-membership': Joins the multicast group specified. Receives a table
---     with fields multiaddr and interface, each containing an IP address;
--- 'ip-drop-membership': Leaves the multicast group specified. Receives a
---     table with fields multiaddr and interface, each containing an IP address.
---
---The method returns 1 in case of success, or nil followed by an error
---message otherwise.
---
---Note: The descriptions above come from the man pages.
---
---@param option unknown
---@return socket.Result<unknown, string>
---@overload fun(self, option: 'dontroute'|'broadcast'|'reuseaddr'|'reuseport'|'ip-multicast-loop'|'ipv6-v6only', value: boolean?): socket.Result<1, string>
---@overload fun(self, option: 'ip-multicast-if', value: string?): socket.Result<1, string>
---@overload fun(self, option: 'ip-multicast-ttl', value: integer?): socket.Result<1, string>
---@overload fun(self, option: 'ip-add-membership', value: socket.UDP_Membership?): socket.Result<1, string>
---@overload fun(self, option: 'ip-drop-membership', value: socket.UDP_Membership?): socket.Result<1, string>
function udp_common:setoption(option, value) end

---Changes the timeout values for the object. By default, the receive and
---receivefrom operations are blocking. That is, any call to the methods will
---block indefinitely, until data arrives. The settimeout function defines a
---limit on the amount of time the functions can block. When a timeout is set
---and the specified amount of time has elapsed, the affected methods give up
---and fail with an error code.
---
---The amount of time to wait is specified as the value parameter, in seconds.
---The nil timeout value allows operations to block indefinitely. Negative
---timeout values have the same effect.
---
---Note: In UDP, the send and sendto methods never block (the datagram is just
---passed to the OS and the call returns immediately). Therefore, the
---settimeout method has no effect on them.
---
---Note: The old timeout method is deprecated. The name has been changed for
---sake of uniformity, since all other method names already contained verbs
---making their imperative nature obvious. 
---
---@param value number|nil
function udp_common:settimeout(value) end

---@class socket.connected: udp_common
connected = udp_common

---Retrieves information about the peer associated with a connected UDP object.
---
---Returns a string with the IP address of the peer, the port number that peer
---is using for the connection, and a string with the family. In case of error,
---the method returns nil.
---
---Note: It makes no sense to call this method on unconnected objects.
---
---@return [string, integer, "inet"|"inet6"]|nil ...
function connected:getpeername() end

---Sends a datagram to the UDP peer of a connected object.
---
---`Datagram` is a string with the datagram contents. The maximum datagram size
---for UDP is 64K minus IP layer overhead. However datagrams larger than the
---link layer packet size will be fragmented, which may deteriorate performance
---and/or reliability.
---
---If successful, the method returns 1. Inb case of error, the method returns
---nil followed by an error message.
---
---Note: In UDP, the `send` method never blocks and the only way it can fail is
---if the underlying transport layer refuses to send a message to the specified
---address (i.e. no interface accepts the address).
---
---@param datagram string
---@return socket.Result<1, string>
function connected:send(datagram) end

---Changes the peer of a UDP object. This method turns an unconnected UDP
---object into a connected UDP object or vice versa.
---
---For connected objects, outgoing datagrams will be sent to the specified
---peer, and datagrams received from other peers will be discarded by the OS.
---Connected UDP objects must use the send and receive methods instead of
---sendto and receivefrom.
---
---Address can be an IP address or a host name. Port is the port number. If
---address is '*' and the object is connected, the peer association is removed
---and the object becomes an unconnected object again. In that case, the port
---argument is ignored.
---
---In case of error the method returns nil followed by an error message. In
---case of success, the method returns 1.
---
---Note: Since the address of the peer does not have to be passed to and from
---the OS, the use of connected UDP objects is recommended when the same peer
---is used for several transmissions and can result in up to 30% performance
---gains.
---
---Note: Starting with LuaSocket 3.0, the host name resolution depends on
---whether the socket was created by socket.udp or socket.udp6. Addresses
---from the appropriate family are tried in succession until the first success
---or until the last failure. 
---
---@param address "*"
---@return socket.Result<1, string>
function connected:setpeername(address) end

---@class socket.unconnected: udp_common
unconnected = udp_common

---Works exactly as the [receive] methid, except it returns the IP address and
---port as extra return values (and is therefore slightly less efficient).
---@param size integer?
---@return [string, string, integer]|[nil, "timeout"] ...
function unconnected:receivefrom(size) end

---Sends a datagram to the specified IP address and port number.
---
---`Datagram` is a string with the datagram contents. The maximum datagram size
---for UDP is 64K minus IP layer overhead. However datagrams larger than the
---link layer packet size will be fragmented, which may deteriorate performance
---and/or reliability. `Ip` is the IP address of the recipient. Host names are
---*not* allowed for performance reasons. `Port` is the port number at the
---recipient.
---
---Note: In UDP, the `send` method never blocks and the only way it can fail is
---if the underlying transport layer refuses to send a message to the specified
---address (i.e. no interface accepts the address).
---
---@param datagram string
---@param ip string
---@param port integer
function unconnected:sendto(datagram, ip, port) end

---Changes the peer of a UDP object. This method turns an unconnected UDP
---object into a connected UDP object or vice versa.
---
---For connected objects, outgoing datagrams will be sent to the specified
---peer, and datagrams received from other peers will be discarded by the OS.
---Connected UDP objects must use the send and receive methods instead of
---sendto and receivefrom.
---
---Address can be an IP address or a host name. Port is the port number. If
---address is '*' and the object is connected, the peer association is removed
---and the object becomes an unconnected object again. In that case, the port
---argument is ignored.
---
---In case of error the method returns nil followed by an error message. In
---case of success, the method returns 1.
---
---Note: Since the address of the peer does not have to be passed to and from
---the OS, the use of connected UDP objects is recommended when the same peer
---is used for several transmissions and can result in up to 30% performance
---gains.
---
---Note: Starting with LuaSocket 3.0, the host name resolution depends on
---whether the socket was created by socket.udp or socket.udp6. Addresses
---from the appropriate family are tried in succession until the first success
---or until the last failure. 
---
---@param address string
---@param port integer
---@return socket.Result<1, string>
function unconnected:setpeername(address, port) end

--- Binds the UDP object to a local address.
---
---Address can be an IP address or a host name. If address is '*' the system
---binds to all local interfaces using the constant INADDR_ANY. If port is 0,
---the system chooses an ephemeral port.
---
---If successful, the method returns 1. In case of error, the method returns
---nil followed by an error message.
---
---Note: This method can only be called before any datagram is sent through
---the UDP object, and only once. Otherwise, the system automatically binds
---the object to all local interfaces and chooses an ephemeral port as soon
---as the first datagram is sent. After the local address is set, either
---automatically by the system or explicitly by setsockname, it cannot be
---changed. 
---
---@param address string
---@param port integer
---@return socket.Result<1, string>
function unconnected:setsockname(address, port) end

---Creates and returns an unconnected UDP object. Unconnected objects support
---the sendto, receive, receivefrom, getoption, getsockname, setoption,
---settimeout, setpeername, setsockname, and close. The setpeername is used to
---connect the object.
---
---In case of success, a new unconnected UDP object returned. In case of error,
---nil is returned, followed by an error message.
---
---Note: The choice between IPv4 and IPv6 happens during a call to sendto,
---setpeername, or sockname, depending on the address family obtained from
---the resolver.
---
---Note: Before the choice between IPv4 and IPv6 happens, the internal socket
---object is invalid and therefore setoption will fail. 
---
---@return socket.Result<socket.unconnected, string>
function socket.udp() end

---Creates and returns an unconnected UDP object. Unconnected objects support
---the sendto, receive, receivefrom, getoption, getsockname, setoption,
---settimeout, setpeername, setsockname, and close. The setpeername is used to
---connect the object.
---
---In case of success, a new unconnected UDP object returned. In case of error,
---nil is returned, followed by an error message.
---
---@return socket.Result<socket.unconnected, string>
function socket.udp4() end

---Creates and returns an unconnected UDP object. Unconnected objects support
---the sendto, receive, receivefrom, getoption, getsockname, setoption,
---settimeout, setpeername, setsockname, and close. The setpeername is used to
---connect the object.
---
---In case of success, a new unconnected UDP object returned. In case of error,
---nil is returned, followed by an error message.
---
---Note: The TCP object returned will have the option "ipv6-v6only" set to true. 
---
---@return socket.Result<socket.unconnected, string>
function socket.udp6() end

---@alias socket.socket socket.master|socket.server|socket.client|socket.connected|socket.unconnected

return socket
