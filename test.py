from socketIO_client import SocketIO, LoggingNamespace

with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
    socketIO.emit('authenticate', "API_KEY IS THIS")
    socketIO.wait(seconds=1)
