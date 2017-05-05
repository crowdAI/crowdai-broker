import json

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
        _message["status"] = False
        _message["message"] = "The following params are required params : %s " % (str(missing_keys))
        _message["response"] = {}
        return {"result": False, "message":_message}
    else:
        return {"result": True}

def config_loader():
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

    return config
