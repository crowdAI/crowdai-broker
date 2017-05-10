import random
import requests
import json
import uuid
import redis
import time
from job_states import JobStates

class CrowdAIBaseChallenge:
    def __init__(self, config, REDIS_POOL):
        self.config = config
        self.redis_pool = REDIS_POOL

    def submit_results_to_crowdai(self, params):
        #TO-DO: Refactor CrowdAI RailsAPI calls into a separate class
        #TO-DO: Dont hardcode -_- !!
        url = self.config["CROWDAI_BASE_URL"]+"/api/external_graders/"
        headers = { 'Authorization': 'Token token=' + self.config["CROWDAI_GRADER_API_KEY"], "Content-Type": "application/vnd.api+json" }
        payload = {
            "challenge_client_name" : self.challenge_id,
            "api_key": params["api_key"],
            "grading_status" : "graded",
            "score" : params["score"],
            "score_secondary" : params["score_secondary"],
            "comment" : params["comment"],
            "media_large" : params["media_large"],
            "media_thumbnail" : params["media_thumbnail"],
            "media_content_type" : params["media_content_type"]
        }
        response = requests.post(url, params=payload, headers=headers, verify=False)
        print response.text
        return response

    def parallel_execute_function(self, function_name, data, extra_params, socketio, dry_run=False):
        """
        Request Params:
            session_token : String
                Unique identifier for a particular session
            function_name : String
                Unique identifier for the relevant function in the challenge
            data : List of JSON Objects
                A List of JSON objects which needs to be passed onto the said function
            extra_params : Object
                Extra Parameters that the said function might need to process
                the data
                * client_response_channel : String
                    socket.io response channel where the client
                    can be relayed the messages from the JobFactory
            socketio : SocketIO Object
                Holds the current session contexxt
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
            _message["job_state"] = JobStates.ERROR
            # To-DO: Add localization to string messages
            _message["message"] = "Function `%s`  unrecognized in context of the %s challenge" % (function_name, challenge_id)
            _message["data"] = {}
            return _message
        else:
            redis_conn = redis.Redis(connection_pool = self.redis_pool)
            respond_to_me_at = self.challenge_id+'::enqueue_job_response::'+ str(uuid.uuid4())
            # The idea of parallel execution is simple. We just enqueue multiple jobs,
            # And ask to receieve all their responses on the same channel.
            # Then we keep rerouting the responses received to the same client_response_channel
            # And delegate the job or organising the responses to the client.
            # As each response has the job_id mentioned, the client should be able to
            # easily make sense of the stream of responses.
            for _idx, _data in enumerate(data):
                _payload = {
                    "respond_to_me_at": respond_to_me_at,
                    "function_name": function_name, #or can also provide "submit"
                    "data" : _data,
                    "data_sequence_no" : _idx #Holds the sequence number in the parallel data array that was passed for execution
                }
                redis_conn.publish(self.challenge_id+'::enqueue_job', json.dumps(_payload))

            #TO-DO: Remove the need of the extra job_response_channel_name variable
            #       Keeping it for now, for consistency and to avoid confusion.
            job_response_channel_name = respond_to_me_at

            # Now keep blpop-ing on the job_response_channel_name
            # until either the Job is complete or there is an error
            total_jobs_processed = 0
            job_responses = []
            for k in range(len(data)):
                job_responses.append(False)

            while True:
                job_response = redis_conn.blpop(job_response_channel_name)
                # The actual response looks like :
                # ('GeccoOptimizationChallenge2017::job_response::d57daf8d-9d96-42ae-ba61-d698f665a753', "{'job_state': 'crowdai.job_state.COMPLETE', 'data': {'score': 45}, 'message': ''}")
                # So we simply ignore the first parameter (the name of job_response_channel_name),
                # and focus on the actual response object
                job_response_blob = json.loads(job_response[1])

                # Relay the response to the client
                socketio.emit(extra_params['client_response_channel'], job_response)
                # Note: time.sleep ensures that the emit message is transferred instantaneously
                # More details : https://github.com/miguelgrinberg/Flask-SocketIO/issues/318
                # If there are performance issues, this can be removed.
                time.sleep(0)
                if job_response_blob['job_state'] == JobStates.COMPLETE:
                    total_jobs_processed += 1
                    job_responses[job_response_blob['data_sequence_no']] = job_response_blob['data']
                if job_response_blob['job_state'] == JobStates.ERROR:
                    total_jobs_processed += 1
                    job_responses[job_response_blob['data_sequence_no']] = job_response_blob['data']

                # The end of a parallel-funciton-execution is now determined by keeping a count
                # of the combined sum of job completions and job-errors.
                # We respond back when all the jobs have terminated (either successfully or unsuccessfully)
                if total_jobs_processed == len(data):
                    return job_responses
            return job_responses

    def execute_function(self, function_name, data, extra_params, socketio, dry_run=False):
        return self.parallel_execute_function(function_name, [data], extra_params, socketio, dry_run=False)[0]
