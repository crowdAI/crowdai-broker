from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import send, emit
from config import Config as config
import uuid
import json

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('authenticate')
def handle_authenticate(args):
    """
        Handles authentication for a particular
        API_KEY and challenge_id pair

        Request Params:
            API_KEY : String
                Holds the API Key of the participant
            challenge_id : String
                Holds the unique identifier for the challenge

        Response Params:
            status : Boolean
                Holds True if the authentication succeeds or False if it doesnot
            message : String
                Holds an optional error message in case of failure of authentication
            session_token : String
                Holds a unique identifier for a particular session
    """
    _message = {}
    _message["status"] = True
    _message["message"] = ""
    _message["session_token"] = str(uuid.uuid4())
    return _message

@socketio.on('close_session')
def close_session(args):
    """
        Closes a session, by registering it in the redis-server

        Request Params:
            session_token : String
                Unique identifier for a particular session

        Response Params:
            status : Boolean
                Holds True if the session is successfully terminated
            message : String
                Holds an optional error message in case of failure of session termination

    """

    _message = {}
    _message["status"] = True
    _message["message"] = ""
    return _message    

@socketio.on('execute_function')
def execute_function(args):
    """
        Executes a particular function from a particular challenge's grader

        Request Params:
            session_token : String
                Unique identifier for a particular session
            challenge_id : String
                Unique identifier for the challenge
            function_name : String
                Unique identifier for the relevant function in the challenge
            data : JSON Object
                JSON object which needs to be passed onto the said function

        Response Params:
            status : Boolean
                Holds True if the operation is successfully executed
            message : String
                Holds an optional error message in case of failure of execution
            response: JSON Object
                JSON object which holds the response of the function
    """

    _message = {}
    _message["status"] = True
    _message["message"] = ""
    _message["response"] = {}
    return _message



if __name__ == '__main__':
    socketio.run(app)
