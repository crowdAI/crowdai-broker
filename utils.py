import json
import redis
from challenges.job_states import JobStates
def validate_request_params(args, expected_keys):
    # Validate request params
    missing_keys = []
    # expected_keys = ["session_token","challenge_id","function_name","data","dry_run"]
    arg_keys = args.keys()
    for _key in expected_keys:
        if _key not in args.keys():
            missing_keys.append(_key)

    if len(missing_keys) > 0:
        _message = {}
        _message["job_state"] = JobStates.ERROR
        _message["message"] = "The following params are required params : %s " % (str(missing_keys))
        _message["body"] = {}
        return {"result": False, "message":_message}
    else:
        return {"result": True}

def validate_parallel_request_params(challenge_id, args, expected_keys):
    config = json.loads(open("config.json").read())
    # Validate request params
    missing_keys = []
    # expected_keys = ["session_token","challenge_id","function_name","data","dry_run"]
    arg_keys = args.keys()
    for _key in expected_keys:
        if _key not in args.keys():
            missing_keys.append(_key)

    _message = {}
    if len(missing_keys) > 0:
        _message["job_state"] = JobStates.ERROR
        _message["message"] = "The following params are required params : %s " % (str(missing_keys))
        _message["body"] = {}
        return {"result": False, "message":_message}
    # Check if the data param is indeed a list, and of length less than a configurable threshold
    elif type(args["data"]) != type([]):
        _message["job_state"] = JobStates.ERROR
        _message["message"] = "Malformed data sent. This function expects a list."
        _message["body"] = {}
        return {"result": False, "message":_message}
    elif len(args["data"]) > config["CHALLENGES"][challenge_id]["max-parallel-jobs"]:
        _message["job_state"] = JobStates.ERROR
        _message["message"] = "This challenge allows a maximum of %d parallel jobs per request" % config["CHALLENGES"][challenge_id]["max-parallel-jobs"]
        _message["body"] = {}
        return {"result": False, "message":_message}
    else:
        _message = {"result": True}

    return _message

def config_loader():
    #TO-DO: Implement a less hacky version of the config loader
    config = json.loads(open("config.json").read())
    barebone_config = config
    #Instantiate Challenge objects
    for _challenge in config["CHALLENGES"].keys():
        # Create the challenge object from the challenge string
        m = __import__("challenges."+_challenge+".class_definition")
        m = getattr(m, _challenge)
        m = getattr(m, "class_definition")
        m = getattr(m, _challenge)

        # Instantiate Challenge specific redis-pool
        REDIS_POOL = redis.ConnectionPool(host=config["CHALLENGES"][_challenge]["redis-host"], port=config["CHALLENGES"][_challenge]["redis-port"], db=0)
        config["CHALLENGES"][_challenge]["instance"] = m(barebone_config, REDIS_POOL)



    return config
