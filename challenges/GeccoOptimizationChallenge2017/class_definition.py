from ..base_challenge import CrowdAIBaseChallenge
import random

class GeccoOptimizationChallenge2017(CrowdAIBaseChallenge):
    def __init__(self):
        CrowdAIBaseChallenge.__init__(self)
        self.challenge_id = "GeccoOptimizationChallenge2017"
        self.supported_functions = ["evaluate"]

    def execute_function(self, function_name, data, dry_run=False):
        """
        Request Params:
            session_token : String
                Unique identifier for a particular session
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
        _message = {}
        if function_name not in self.supported_functions:
            _message["status"] = False
            # To-DO: Add localization to string messages
            _message["message"] = "Function `%s`  unrecognized in context of the %s challenge" % (function_name, challenge_id)
            _message["response"] = {}
            return _message
        else:
            if function_name == "evaluate":
                try:
                    response = self._evaluate(data, dry_run)
                    _message["response"] = response
                    _message["status"] = True
                    _message["message"] = ""
                except e:
                    _message["status"] = False
                    _message["message"] = str(e)
                    _message["response"] = {}
                return _message

    def _evaluate(self, data, dry_run=False):
        """
            Evaluates the
        """
        if dry_run == True:
            # TO-DO: Replace with a valid random sampling
            return [random.sample(range(30), 10) for x in range(10)]
        else:
            #TO-DO: Replace with actual execution
            return [random.sample(range(30), 10) for x in range(10)]
