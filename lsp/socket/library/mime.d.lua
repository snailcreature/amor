---@meta

---@class mime
mime = {}

---@alias mime.dos "\x0D\x0A" `"\x0D\x0A"`
---@type mime.dos `"\x0D\x0A"`
mime.dos = "\x0D\x0A"

---@alias mime.cr "\x0D" `"\x0D"`
---@type mime.cr `"\x0D"`
mime.cr = "\x0D"

---@alias mime.lf "\x0A" `"\x0A"`
---@type mime.lf `"\x0A"`
mime.lf = "\x0A"

---@alias mime.marker # end-of-line marker
--- | mime.dos # `"\x0D\x0A"`
--- | mime.cr  # `"\x0D"`
--- | mime.lf  # `"\x0A"`

---Returns a filter that decodes data from a given transfer content encoding.
---
---@param format "base64"|"quoted-printable"
---@return ltn12.filter.filter
function mime.decode(format) end

---Returns a filter that encodes data according to a given transfer content
---encoding.
---
---Although both transfer content encoding specify a limit for the line length,
---the encoding filters do *not* break text into lines (for added flexibility).
---
---Note: Text data *has* to be converted to canonic form *before* being encoded.
---
---@param format "base64"
---@return ltn12.filter.filter
function mime.encode(format) end

---Returns a filter that encodes data according to a given transfer content
---encoding.
---
---In the quoted-printable case, the user can specify whether the data is
---textual or binary by passing the mode strings `"text"` or `"binary"`. Mode
---defaults to `"text"`.
---
---Although both transfer content encoding specify a limit for the line length,
---the encoding filters do *not* break text into lines (for added flexibility).
---
---Note: Text data *has* to be converted to canonic form *before* being encoded.
---
---@param format "quoted-printable"
---@param mode "text"|"binary"? Defaults to `"text"`
---@return ltn12.filter.filter
function mime.encode(format, mode) end

---Converts most common end-of-line markers to a specific given marker.
---
---Marker is the new marker. It defaults to CRLF, the canonic end-of-line marker
---defined by the MIME standard.
---
---The function returns a filter that performs the conversion.
---
---Note: There is no perfect solution to this problem. Different end-of-line
---markers are an evil that will probably plague developers forever. This
---function, however, will work perfectly for text created wit any of the most
---common end-of-line markers, i.e. the Mac OS (CR), the Unix (LF), or the DOS
---(CRLF) conventions. Even if the data has mixed end-of-line markers, the
---function will still work well, although it doesn't guarantee that the number
---of empty lines will be correct.
---
---@param marker mime.marker?
---@return ltn12.filter.filter
function mime.normalize(marker) end

---Creates and returns a filter that performs stuffing of SMTP messages.
---
---Note: the `smtp.send` function uses this filter automatically. You don't need
---to chain it with your source, or apply it to your message body.
---
---@return ltn12.filter.filter
function mime.stuff() end

---Returns a filter that breaks data into lines.
---
---The `"text"` line-wrap filter simply breaks text into lines by inserting CRLF
---end-of-line markers at appropriate positions.
---
---Note: To break into lines with a different end-of-line convention, apply a
---normalization filter after the line break filter.
---
---@param format "text"
---@param length integer? Defaults to `76`
---@return ltn12.filter.filter
function mime.wrap(format, length) end

---Returns a filter that breaks data into lines.
---
---The `"base64"` line-wrap filter works just like the default `"text"`
---line-wrap filter with default length. The function can also wrap
---`"quoted-printable"` lines, taking care not to break lines in the middle of
---an escaped character. In that case, the line length is fixed at `76`.
---
---Note: To break into lines with a different end-of-line convention, apply a
---normalization filter after the line break filter.
---
---@param format "base64"|"quoted-printable"
---@return ltn12.filter.filter
function mime.wrap(format) end

---Low-level filter to perform Base64 encoding.
---
---`A` is the encoded version of the largest prefix of `C..D` that can be
---encoded unambiguously. `B` has the remaining bytes of `C..D`, *before*
---encoding. If `D` is `nil`, `A` is padded with the encoding of the remaining
---bytes of `C`.
---
---Note: The simplest use of this function is to encode a string into it's Base64
---transfer content encoding.
---
---@generic A: string Encoded version of the largest prefix of `C..D` that can be encoded unambiguously
---@generic B: string Remaining bytes of `C..D`, *before* encoding.
---@param C string
---@param D string?
---@return [A, B]
function mime.b64(C, D) end

---Low-level filter to perform SMTP stuffing and enable transmission of messages
---containing the sequence "CRLF.CRLF".
---
---`A` is the stuffed version of `B`. `n` gives the number of characters from
---the sequence CRLF seen in the end of `B`. `m` should tell the same, but for
---the previous chunk.
---
---Note: The message body is defined to being with an implicit CRLF. Therefore,
---to stuff a message correctly, the first `m` should have the value `2`.
---
---Note: The `smtp.send` function uses this filter automatically. You don't need
---to apply it again.
---
---@generic A: string
---@generic n: integer
---@param m integer
---@param B string?
---@return [A, n]
function mime.dot(m, B) end

---Low-level filter to perform end-of-line marker translation. For each chunk,
---the function needs to know if the last character of the previous chunk could
---be part of an end-of-line marker or not. This is the context the function
---receives besides the chunk. An updated version of the context is returned
---after each new chunk.
---
---`A` is the translated version of `D`. `C` is the ASCII value of the last
---character of the previous chunk, if it was a candidate for line break, or 0
---otherwise. `B` is the same as `C`, but for the current chunk. `Marker` gives
---the new end-of-line marker and defaults to CRLF.
---
---@generic A: string
---@generic B: string|0
---@param C string|0
---@param D string?
---@param marker mime.marker?
---@return [A, B]
function mime.eol(C, D, marker) end

---Low-level filter to perform Quoted-Printable encoding.
---
---`A` is the encoded version of the largest prefix of `C..D` that can be
---encoded unambiguously. `B` has the remaining bytes of `C..D`, *before*
---encoding. If `D` is `nil`, `A` is padded with the encoding of the remaining
---bytes of `C`. Throughout encoding, occurrences of CRLF are replaced by the
---`marker`, which itself defaults to CRLF.
---
---Note: the simplest use of this function is to encode a string into its
---Quoted-Printable transfer content encoding.
---
---@generic A: string
---@generic B: string
---@param C string
---@param D string?
---@param marker mime.marker?
---@return [A, B]
function mime.qp(C, D, marker) end

---Low-level filter to break Quoted-Printable text into lines.
---
---`A` is a copy of `B`, broken into lines of at most `length` bytes (defaults
---to 76). `n` should tell how many bytes are left for the first line of `B` and
---`m` returns the number of bytes left in the last line of `A`.
---
---Note: Besides breaking text into lines, this function makes sure the line
---breaks don't fall in the middle of an escaped character combination. Also,
---this function only breaks lines that are bigger than `length` bytes.
---
---@generic A: string
---@generic m: integer
---@param n integer
---@param B string?
---@param length integer?
---@return [A, m]
function mime.qpwrp(n, B, length) end

return mime
