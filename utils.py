
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
