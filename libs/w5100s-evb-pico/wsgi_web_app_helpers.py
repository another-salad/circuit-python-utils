"""Generic helpers for WSGI apps"""

import json


class HTTPStatusCodes:
    """
    Generic Status codes to be used by WSGI apps.
    Maybe one day Circuit Python will have enums :'(
    """

    OK = "200 OK"
    BAD_REQUEST = "400 BAD REQUEST"
    NOT_FOUND = "404 NOT FOUND"
    INTERNAL_SERVER_ERROR = "500 INTERNAL SERVER ERROR"
    NOT_IMPLEMENTED = "501 NOT IMPLEMENTED"


def web_response_wrapper(func, *args, **kwargs):
    """
    Wraps a function call in a try except so a HTTP status code is always returned.
    If the function returns a dictionary it is added to the response json.
    """
    status_code = HTTPStatusCodes.OK
    response = {"error": 0}
    try:
        if not callable(func):
            raise Exception("Implementation error: Must be callable.")

        res = func(*args, **kwargs)
        if isinstance(res, dict):
            response.update(**res)

    except Exception as exc:
        status_code = HTTPStatusCodes.INTERNAL_SERVER_ERROR
        response["error"] = 1
        response["traceback"] = repr(exc)

    return (
        status_code,
        [("Content-type", "application/json; charset=utf-8")],
        [json.dumps(response).encode("UTF-8")]
    )
