from flask import Flask
from flask_socketio import SocketIO
from flask import copy_current_request_context
from flask_socketio import send, emit

from utils import config_loader, validate_request_params, validate_parallel_request_params
from challenges.job_states import JobStates

import requests

import uuid
import json

import time

"""
Note: Adding eventlet and monkey_patching it to ensure that emit messages are not
    accumulated and sent out in bursts
"""
import eventlet
eventlet.monkey_patch()

"""
Load config
"""
config = config_loader()

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
            client_version : String
                Holds the version number of the crowdai client

        Response Params:
            status : Boolean
                Holds True if the authentication succeeds or False if it doesnot
            message : String
                Holds an optional error message in case of failure of authentication
            session_token : String
                Holds a unique identifier for a particular session
    """
    validation = validate_request_params(args, ["API_KEY", "challenge_id", "client_version"])
    if not validation["result"]:
        return validation["message"]
    API_KEY = args["API_KEY"]
    challenge_id = args["challenge_id"]
    client_version = args["client_version"]

    if challenge_id not in config["CHALLENGES"].keys():
        _message = {}
        _message["status"] = False
        _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
        _message["response"] = {}
        return _message
    else:
        if config['DEBUG_MODE']:
            _message = {}
            _message["status"] = True
            _message["message"] = "DEBUG_MODE: Ignoring authentication with the crowdAI Server"
            _message["session_token"] = str(uuid.uuid4())
            # print args["client_version"]
            # return {
            #         "status": False,
            #         "message": "Not cool :("
            #         }

            return _message

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
            api_key : String
                Participant's API Key
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
            parallel : Boolean
                Boolean Variable which states if multiple jobs are to be parallely
                executed

        Response Params:
            job_state : String
                Holds the type of the job event as described in the JobStates Class
            message : String
                Optional Message
            data : JSON Object
                JSON object which holds the response of the function
                Look up the function definitions for more information on the structure
                of the data
    """
    try:
        # Validate request params
        validation = validate_request_params(args, ["response_channel", "session_token", "api_key", "challenge_id","function_name","data","dry_run", "parallel"])
        if not validation["result"]:
            return validation["message"]

        client_response_channel = args["response_channel"]
        session_token = args["session_token"]
        api_key = args["api_key"]
        challenge_id = args["challenge_id"]
        function_name = args["function_name"]
        data = args["data"]
        dry_run = args["dry_run"]
        parallel = args["parallel"]

        if parallel == True:
            #Validate again if its a parallel job processing request
            validation = validate_parallel_request_params(challenge_id, args, ["response_channel", "session_token", "api_key", "challenge_id","function_name","data","dry_run", "parallel"])
            if not validation["result"]:
                return validation["message"]


        # TO-DO: Validate Session. Expire session after 48 hours
        extra_params = {
            "session_token" : session_token,
            "api_key": api_key
        }

        if challenge_id not in config["CHALLENGES"].keys():
            _message = {}
            _message["job_state"] = JobStates.ERROR
            _message["message"] = "Unrecognized Challenge : %s. \n Please check the `challenge_id` again and/or update your client." % challenge_id
            _message["data"] = {}

            return _message
        else:
            # The actual response channel is prepended with the session_token to discourage session hijacking attempts
            extra_params["client_response_channel"] = session_token+"::"+client_response_channel
            if parallel == False:
                config["CHALLENGES"][challenge_id]["instance"].execute_function(function_name, data, extra_params, socketio, dry_run)
            else:
                config["CHALLENGES"][challenge_id]["instance"].parallel_execute_function(function_name, data, extra_params, socketio, dry_run)
            _result = {}
            _result["job_state"] = JobStates.COMPLETE
            _result["data"] = {}
            _result["message"] = ""
            return _result
    except Exception as e:
            _message = {}
            _message["job_state"] = JobStates.ERROR
            _message["message"] = str(e)
            _message["data"] = {}
            return _message

if __name__ == '__main__':
    socketio.run(app, host=config['SOCKETIO-HOST'], port=config['SOCKETIO-PORT'])
