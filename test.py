from socketIO_client import SocketIO, LoggingNamespace
import time

challenge_id = "GeccoOptimizationChallenge2017"
session_token = "askjdhaskhdksahdkjhsakjh"

connection = SocketIO('localhost', 5000, LoggingNamespace)

#Authenticate
def authenticate(connection):
    AUTHENTICATE_TIMEOUT=5
    def on_authenticate_response(*args):
        print('on_authenticate_response', args)

    response = connection.emit('authenticate', {"API_KEY":"API_KEY IS THIS",
                                   "challenge_id": "GeccoOptimizationChallenge2017"},
                                   callbacks=on_authenticate_response)
    connection.wait_for_callbacks(seconds=AUTHENTICATE_TIMEOUT)
    # print response

authenticate(connection)
#
# with SocketIO('localhost', 5000, LoggingNamespace) as socketIO:
#     def on_authenticate_response(*args):
#         print('on_authenticate_response', args)
#         # session_token = args[1][0]["session_token"]
#         def on_execute_function_response(*args):
#             print "Received response......"
#             print('on execute function response ', args)
#
#         socketIO.emit('execute_function',
#                         {   "session_token": session_token,
#                             "challenge_id": challenge_id,
#                             "function_name": "evaluate",
#                             "data": [100, 200, 300],
#                             "dry_run" : True
#                         }, on_execute_function_response)
#
#     socketIO.emit('authenticate', {"API_KEY":"API_KEY IS THIS",
#                                    "challenge_id": "GeccoOptimizationChallenge2017"},
#                                 on_authenticate_response)
#     # socketIO.wait(seconds=1)
#
#
#     socketIO.wait(seconds=1)
