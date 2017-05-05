from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import send, emit

from utils import validate_request_params

import requests

import uuid
import json

import time

"""
Load config
"""
#TO-DO: Implement a less hacky version of the config loader
config = json.loads(open("config.json").read())
barebone_config = config
#Instantiate Challenge objects
for _challenge in config["CHALLENGES"].keys():
    m = __import__("challenges."+_challenge+".class_definition")
    m = getattr(m, _challenge)
    m = getattr(m, "class_definition")
    m = getattr(m, _challenge)
    config["CHALLENGES"][_challenge]["instance"] = m(barebone_config)

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

    if challenge_id not in config["CHALLENGES"].keys():
        _message = {}
        _message["status"] = False
        _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
        _message["response"] = {}

        return _message
    else:
        # TO-DO: Add actual authentication
        def _authenticate(API_KEY):
            #TO-DO: Refactor CrowdAI RailsAPI calls into a separate class
            url = config["CROWDAI_BASE_URL"]+"/api/external_graders/"+API_KEY
            headers = { 'Authorization': 'Token token=' + config["CROWDAI_GRADER_API_KEY"], "Content-Type": "application/vnd.api+json" }
            return requests.get(url, headers=headers, verify=False)

        authentication_response = _authenticate(API_KEY)
        _message = {}
        #TO-DO: Add explanation for the status code comparison
        _message["status"] = authentication_response.status_code == 200
        _message["message"] = json.loads(authentication_response.text)["message"]
        _message["session_token"] = str(uuid.uuid4())
        #TO-DO: Setup internal session token
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
            response_channel : String
                The name of the response channel where the server replies back
                about the final result and the progress in the meantime
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
    validation = validate_request_params(args, ["response_channel", "session_token","challenge_id","function_name","data","dry_run"])
    if not validation["result"]:
        return validation["message"]

    response_channel = args["response_channel"]
    session_token = args["session_token"]
    challenge_id = args["challenge_id"]
    function_name = args["function_name"]
    data = args["data"]
    dry_run = args["dry_run"]

    # TO-DO: Validate Session. Expire session after 48 hours

    if challenge_id not in config["CHALLENGES"].keys():
        _message = {}
        _message["status"] = False
        _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
        _message["response"] = {}

        return _message
    else:
        result = config["CHALLENGES"][challenge_id]["instance"].execute_function(function_name, data, dry_run)
        #Enqueue Job
        #Listen on Output Channel
        #Relay messages to the client until job complete
        #Stop listening on Output Channel in case of job complete or error
        result["is_complete"] = False
        result["progress"] = 0
        for k in range(100):
            if k==99:
                result["is_complete"] = True
                result["progress"] = 1
                emit(response_channel, result)
                #In case of error, "emit" result with status False,
                # and return empty value to end this call
            else:
                result["is_complete"] = False
                result["progress"] = k*1.0/100
                # emit(response_channel, result)
                #In case of error, "emit" result with status False,
                # and return empty value to end this call
        return {}
        # return _message


if __name__ == '__main__':
    socketio.run(app)
