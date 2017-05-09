from ..base_challenge import CrowdAIBaseChallenge
import random
import requests
import json
import uuid

from flask_socketio import send, emit


class GeccoOptimizationChallenge2017(CrowdAIBaseChallenge):
    def __init__(self, config, REDIS_POOL):
        CrowdAIBaseChallenge.__init__(self, config, REDIS_POOL)
        self.challenge_id = "GeccoOptimizationChallenge2017"
        self.supported_functions = ["evaluate", "submit"]

    def execute_function(self, function_name, data, extra_params, dry_run=False):
        """
        Request Params:
            session_token : String
                Unique identifier for a particular session
            function_name : String
                Unique identifier for the relevant function in the challenge
            data : JSON Object
                JSON object which needs to be passed onto the said function
            extra_params : Object
                Extra Parameters that the said function might need to process
                the data
                * client_response_channel : String
                    socket.io response channel where the client
                    can be relayed the messages from the JobFactory
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
        _message = {}
        if function_name not in self.supported_functions:
            _message["status"] = False
            # To-DO: Add localization to string messages
            _message["message"] = "Function `%s`  unrecognized in context of the %s challenge" % (function_name, challenge_id)
            _message["response"] = {}
            return _message
        else:
            if function_name == "evaluate":

                # try:
                #     response = self._evaluate(data, extra_params, dry_run)
                #     _message["response"] = response
                #     _message["status"] = True
                #     _message["message"] = ""
                # except e:
                #     _message["status"] = False
                #     _message["message"] = str(e)
                #     _message["response"] = {}
                # return _message
            # if function_name == "submit":
            #     response = self._submit(data, extra_params, dry_run)
            #     if response["submission_id"] != None:
            #         _message["response"] = response["submission_id"]
            #         _message["status"] = True
            #         _message["message"] = response["message"]
            #     else:
            #         _message["status"] = False
            #         _message["message"] = response["message"]
            #         _message["response"] = {}
            #     return _message


    def _evaluate(self, data, extra_params, dry_run=False):
        """
            Evaluates the
        """
        if dry_run == True:
            # TO-DO: Replace with a valid random sampling
            return [random.sample(range(30), 10) for x in range(10)]
        else:
            #TO-DO: Replace with actual execution
            return [random.sample(range(30), 10) for x in range(10)]

    def _submit(self, data, extra_params, dry_run=False):
        """
            Evaluates a value and submits the score to CrowdAI
        """
        for k in range(10):
            _message = {}
            _message["response"] = [1,2,3,4,5,6,7,8,9]
            _message["status"] = True
            _message["message"] = "On the Grader...."
            _message["is_complete"] = False
            _message["progress"] = k*1.0/100
            emit(extra_params['response_channel'], _message)
        # emit(self.session_token+"::"+self.response_channel, result)
        #TO-DO: Implement dry_run

        extra_params["score"] = random.randint(0, 100)*1.0/100,
        extra_params["score_secondary"] = random.randint(0, 100)*1.0/100,
        extra_params["comment"] = "Ohhhh Yeahhhhh"
        extra_params["media_large"] = "http://cdn.zmescience.com/wp-content/uploads/2011/11/celegans-1.jpg"
        extra_params["media_thumbnail"] = "http://cdn.zmescience.com/wp-content/uploads/2011/11/celegans-1.jpg"
        extra_params["media_content_type"] = "image/jpeg"

        submit_response = self.submit_results_to_crowdai(extra_params)
        data = json.loads(submit_response.text)
        if submit_response.status_code == 202:
            pass
        else:
            data["submission_id"] = None
        return data
