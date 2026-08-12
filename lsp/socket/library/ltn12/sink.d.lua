---@meta

---@class ltn12.sink
ltn12.sink = {}

---Final node in an LTN12 network, sending data to its final location.
---
---@class ltn12.sink.sink: function
ltn12.sink.sink = {}

---Creates and returns a new sink that passes data through a filter before
---sending to a given sink.
---
---@param filter ltn12.filter.filter
---@param sink ltn12.sink.sink
---@return ltn12.sink.sink
function ltn12.sink.chain(filter, sink) end

---Creates and returns a sink that aborts transmission with the error message.
---
---@param message string
---@return ltn12.sink.sink
function ltn12.sink.error(message) end

---Creates a sink that sends data to a file.
---
---The function returns a sink that sends all data to the given handle and
---closes the file when done, or a sink that aborts the transmission with the
---error message.
---
---Designed to accept `io.open` as a single parameter.
---
---@param handle file*? File handle
---@param message string? Reason for failure if handle is nil
---@return ltn12.sink.sink
function ltn12.sink.file(handle, message) end

---Returns a sink that ignores all data it receives.
---
---@return ltn12.sink.sink
function ltn12.sink.null() end

---Creates a sink that stores all chunks in a table. The chunks can later be
---efficiently concatenated into a single string.
---
---Returns the sink and the table used to store the chunks.
---
---@param table table? Table used to store the chunks. If nil, function creates a table
---@return [ltn12.sink.sink, table]
function ltn12.sink.table(table) end
