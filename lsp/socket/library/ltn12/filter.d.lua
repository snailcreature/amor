---@meta

---@class ltn12.filter
ltn12.filter = {}

---Function that accepts successive chunks of input and produces successive
---chunks of output.
---
---@class ltn12.filter.filter: function
ltn12.filter.filter = {}

---Returns a filter that passes all data it receives through each of a series of
---given filters.
---
---@param ... ltn12.filter.filter Filter functions
---@return ltn12.filter.filter
function ltn12.filter.chain(...) end

---Returns a high-level filter that cycles through a low-level fulter by passing
---it each chunk and updating a context between calls.
---
---@param low ltn12.filter.filter Low-level filter to be cycled
---@param ctx unknown Initial context
---@param extra unknown Any extra argument the low-level filter might take
---@return ltn12.filter.filter
function ltn12.cycle(low, ctx, extra) end
