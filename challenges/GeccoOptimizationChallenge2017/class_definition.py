from ..base_challenge import CrowdAIBaseChallenge
from ..job_states import JobStates
import json

class GeccoOptimizationChallenge2017(CrowdAIBaseChallenge):
    def __init__(self, config, REDIS_POOL):
        CrowdAIBaseChallenge.__init__(self, config, REDIS_POOL)
        self.challenge_id = "GeccoOptimizationChallenge2017"
        self.supported_functions = ["evaluate", "submit"]
        self.submit_function_name = "evaluate"

    def execute_submit(self, data, extra_params, socketio):
        response = self.execute_function("submit", data, extra_params, socketio)

        payload = {
            "challenge_client_name" : self.challenge_id,
            "api_key": extra_params["api_key"],
            "grading_status" : "graded",
            "score" : response['score'],
            "score_secondary" : response['secondary_score'],
            "comment" : "Placeholder Comment",#TODO : Implement Comments
            "media_large" : response["media_large"],
            "media_thumbnail" : response["media_thumbnail"],
            "media_content_type" : response["media_content_type"]}

        _status_response = {}
        _status_response["job_state"] = JobStates.INFO
        _status_response["job_id"] = ""
        _status_response["data_sequence_no"] = -1
        _status_response["message"] = "Submitting Score to CrowdAI Leaderboard..."

        socketio.emit(extra_params['client_response_channel'], json.dumps(_status_response))

        submit_response = self.submit_results_to_crowdai(payload)
        data = json.loads(submit_response.text)

        if submit_response.status_code == 202:
            _status_response = {}
            _status_response["job_state"] = JobStates.COMPLETE
            _status_response["job_id"] = ""
            _status_response["data_sequence_no"] = -1
            _status_response["message"] = "Successfully uploaded score to crowdAI.  Score : "+str(response['score'])

            socketio.emit(extra_params['client_response_channel'], json.dumps(_status_response))
        else:
            _status_response = {}
            _status_response["job_state"] = JobStates.ERROR
            _status_response["job_id"] = ""
            _status_response["data_sequence_no"] = -1
            _status_response["message"] = "Unable to upload to crowdAI. \n "+submit_response.text+"\nPlease contact the crowdAI admins."

            socketio.emit(extra_params['client_response_channel'], json.dumps(_status_response))

        return response
