---@meta

---@class ltn12.source
ltn12.source = {}

---Initial node in an LTN12 network, producing data to be manipulated.
---
---@class ltn12.source.source: function
ltn12.source.source = {}

---Creates a new source that produces the concatenation of the data produced by
---a number of sources.
---
---@param ... ltn12.source.source
---@return ltn12.source.source
function ltn12.source.cat(...) end

---Creates a new source that passes the data through a filter before returning it.
---
---@param source ltn12.source.source
---@param filter ltn12.filter.filter
---@return ltn12.source.source
function ltn12.source.chain(source, filter) end

---Creates and returns an empty source.
---
---@return ltn12.source.source
function ltn12.source.empty() end

---Creates and returns a source that aborts transmission with error message.
---
---@param message string
---@return ltn12.source.source
function ltn12.source.error(message) end

---Creates a source that produces the contents of a file.
---
---Designed to accept the result of `io.open` as a single parameter.
---
---The function returns a source that reads chunks of data from given handle and
---returns it to the user, closing the file when done, or a source that aborts
---the transmission with the error message.
---
---@param handle file*?
---@param message string?
---@return ltn12.source.source
function ltn12.source.file(handle, message) end

---Creates and returns a simple source given a fancy source.
---
---@param source ltn12.source.source
---@return ltn12.source.source
function ltn12.source.simplify(source) end

---Creates and returns a source that produces the contents of a string, chunk by
---chunk.
---
---@param string string
---@return ltn12.source.source
function ltn12.source.string(string) end

---Creates and returns a source that produces the numerically-indexed values of
---a table successively beginning at 1. The source returns nil (end-of-stream)
---whenever a nil value is produced by the current index, which proceeds forward
---regardless.
---
---@param table table
---@return ltn12.source.source
function ltn12.source.table(table) end
