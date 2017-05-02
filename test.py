from socketIO_client import SocketIO, LoggingNamespace

with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
    def on_authenticate_response(*args):
        print('on_authenticate_response', args)
    socketIO.emit('authenticate', {"api_key":"API_KEY IS THIS",
                                   "challenge_id": "Challenge_id"},
                                on_authenticate_response)
    socketIO.wait(seconds=1)
