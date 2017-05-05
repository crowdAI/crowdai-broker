import requests
class CrowdAIBaseChallenge:
    def __init__(self, config):
        self.config = config

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
        return requests.post(url, params=payload, headers=headers, verify=False)
