---@meta

---@class ltn12.pump
ltn12.pump = {}

---Pushes data through a LTN12 network from
---source to sink
---
---@class ltn12.pump.pump: function 
ltn12.pump.pump = {}

---Pumps all data from a source to a sink.
---
---If successful, the function returns a value that evaluates to true. In case 
---of error, the function returns a false value, followed by an error message.
---
---@param source ltn12.source.source
---@param sink ltn12.sink.sink
---@return [true, nil]|[false, string]
function ltn12.pump.all(source, sink) end

---Pumps one chunk of data from a source to a sink.
---
---If successful, the function returns a value that evaluates to true. In case 
---of error, the function returns a false value, followed by an error message.
---
---@param source ltn12.source.source
---@param sink ltn12.sink.sink
---@return [true, nil]|[false, string]
function ltn12.pump.step(source, sink) end
