---@meta

---@class socket.ftp
socket.ftp = {}

---Downloads the contents of a URL and returns it as a string
---
---@param url string Conforms to RFC 1738; `"[ftp://][<user>[:<password>]@]<host>[:<port>][/<path>][type=a|i]"`
---@return [string, nil]|[nil, string]
function socket.ftp.get(url) end

---If the argument of the get function is a table, the function expects at least
---the fields host, sink, and one of argument or path (argument takes precedence).
---Host is the server to connect to. Sink is the simple LTN12 sink that will receive
---the downloaded data. Argument or path give the target path to the resource in
---the server. The optional arguments are the following:
--- 
--- user, password: User name and password used for authentication. Defaults to "ftp:anonymous@anonymous.org";
--- command: The FTP command used to obtain data. Defaults to "retr", but see example below;
--- port: The port to used for the control connection. Defaults to 21;
--- type: The transfer mode. Can take values "i" or "a". Defaults to whatever is the server default;
--- step: LTN12 pump step function used to pass data from the server to the sink. Defaults to the LTN12 pump.step function;
--- create: An optional function to be used instead of socket.tcp when the communications socket is created.
---
---@param host string
---@param sink ltn12.sink.sink
---@param argument string
---@param user string?
---@param password string?
---@param command string?
---@param port integer?
---@param type string?
---@param step ltn12.pump.pump
---@param create function
---@return [1, nil]|[nil, string]
function socket.ftp.get(host, sink, argument, user, password, command, port, type, step, create) end

---If the argument of the get function is a table, the function expects at least
---the fields host, sink, and one of argument or path (argument takes precedence).
---Host is the server to connect to. Sink is the simple LTN12 sink that will receive
---the downloaded data. Argument or path give the target path to the resource in
---the server. The optional arguments are the following:
---  
--- user, password: User name and password used for authentication. Defaults to "ftp:anonymous@anonymous.org";
--- command: The FTP command used to obtain data. Defaults to "retr", but see example below;
--- port: The port to used for the control connection. Defaults to 21;
--- type: The transfer mode. Can take values "i" or "a". Defaults to whatever is the server default;
--- step: LTN12 pump step function used to pass data from the server to the sink. Defaults to the LTN12 pump.step function;
--- create: An optional function to be used instead of socket.tcp when the communications socket is created.
---
---@param host string
---@param sink ltn12.sink.sink
---@param path string
---@param user string?
---@param password string?
---@param command string?
---@param port integer?
---@param type string?
---@param step ltn12.pump.pump
---@param create function
---@return [1, nil]|[nil, string]
function socket.ftp.get(host, sink, path, user, password, command, port, type, step, create) end

---Uploads a string of content to the URL.
---
---@param url string
---@param content string
---@return [1, nil]|[nil, string]
function socket.ftp.put(url, content) end

---If the argument of the put function is a table, the function expects at least
---the fields host, source, and one of argument or path (argument takes precedence).
---Host is the server to connect to. Source is the simple LTN12 source that will
---provide the contents to be uploaded. Argument or path give the target path to
---the resource in the server. The optional arguments are the following:
--- 
--- user, password: User name and password used for authentication. Defaults to "ftp:anonymous@anonymous.org";
--- command: The FTP command used to send data. Defaults to "stor", but see example below;
--- port: The port to used for the control connection. Defaults to 21;
--- type: The transfer mode. Can take values "i" or "a". Defaults to whatever is the server default;
--- step: LTN12 pump step function used to pass data from the server to the sink. Defaults to the LTN12 pump.step function;
--- create: An optional function to be used instead of socket.tcp when the communications socket is created.
---
---@param host string
---@param source ltn12.sink.sink
---@param argument string
---@param user string?
---@param password string?
---@param command string?
---@param port integer?
---@param type string?
---@param step ltn12.pump.pump
---@param create function
---@return [1, nil]|[nil, string]
function socket.ftp.put(host, source, argument, user, password, command, port, type, step, create) end

---If the argument of the put function is a table, the function expects at least
---the fields host, source, and one of argument or path (argument takes precedence).
---Host is the server to connect to. Source is the simple LTN12 source that will
---provide the contents to be uploaded. Argument or path give the target path to
---the resource in the server. The optional arguments are the following:
--- 
--- user, password: User name and password used for authentication. Defaults to "ftp:anonymous@anonymous.org";
--- command: The FTP command used to send data. Defaults to "stor", but see example below;
--- port: The port to used for the control connection. Defaults to 21;
--- type: The transfer mode. Can take values "i" or "a". Defaults to whatever is the server default;
--- step: LTN12 pump step function used to pass data from the server to the sink. Defaults to the LTN12 pump.step function;
--- create: An optional function to be used instead of socket.tcp when the communications socket is created.
---
---@param host string
---@param source ltn12.sink.sink
---@param path string
---@param user string?
---@param password string?
---@param command string?
---@param port integer?
---@param type string?
---@param step ltn12.pump.pump
---@param create function
---@return [1, nil]|[nil, string]
function socket.ftp.put(host, source, path, user, password, command, port, type, step, create) end

return socket.ftp
