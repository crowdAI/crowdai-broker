from ..base_challenge import CrowdAIBaseChallenge

class GeccoOptimizationChallenge2017(CrowdAIBaseChallenge):
    def __init__(self, config, REDIS_POOL):
        CrowdAIBaseChallenge.__init__(self, config, REDIS_POOL)
        self.challenge_id = "GeccoOptimizationChallenge2017"
        self.supported_functions = ["evaluate", "submit"]
