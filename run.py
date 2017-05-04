from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import send, emit
from config import Config as config

from utils import validate_request_params

import uuid
import json

import time

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
    validation = validate_request_params(args, ["API_KEY", "challenge_id"])
    if not validation["result"]:
        return validation["message"]

    API_KEY = args["API_KEY"]
    challenge_id = args["challenge_id"]

    if challenge_id not in config.CHALLENGES.keys():
        _message = {}
        _message["status"] = False
        _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
        _message["response"] = {}

        return _message
    else:
        # TO-DO: Add actual authentication
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
    validation = validate_request_params(args, ["session_token"])
    if not validation["result"]:
        return validation["message"]
    session_token = args["session_token"]

    # TO-DO : Add actual session termination

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
            dry_run : Boolean
                Boolean Variable which states if the operation is needed to be
                actually executed, or randomly generated but semantically relevant
                response is supposed to be returned.

        Response Params:
            status : Boolean
                Holds True if the operation is successfully executed
            message : String
                Holds an optional error message in case of failure of execution
            response: JSON Object
                JSON object which holds the response of the function
    """
    #TO-DO: Add a separate `type` param to communicate the "progress of execution"

    # Validate request params
    validation = validate_request_params(args, ["session_token","challenge_id","function_name","data","dry_run"])
    if not validation["result"]:
        return validation["message"]

    session_token = args["session_token"]
    challenge_id = args["challenge_id"]
    function_name = args["function_name"]
    data = args["data"]
    dry_run = args["dry_run"]

    # TO-DO: Validate Session. Expire session after 48 hours

    if challenge_id not in config.CHALLENGES.keys():
        _message = {}
        _message["status"] = False
        _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
        _message["response"] = {}

        return _message
    else:
        _message = config.CHALLENGES[challenge_id]["instance"].execute_function(function_name, data, dry_run)
        return _message


if __name__ == '__main__':
    socketio.run(app)
