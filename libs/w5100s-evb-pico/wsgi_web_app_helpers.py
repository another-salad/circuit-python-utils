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


class ErrorCodes:
    OK = 0
    INPUT_ERROR = 1
    INTERNAL_ERROR = 2


def bad_request(traceback_response):
    """Returns an error code and traceback on a bad request error"""
    response = {}
    response["error"] = ErrorCodes.INPUT_ERROR
    response["traceback"] = traceback_response
    return response, HTTPStatusCodes.BAD_REQUEST


def internal_server_error(traceback_response):
    """Returns an error code and traceback on a internal server error"""
    response = {}
    response["error"] = ErrorCodes.INTERNAL_ERROR
    response["traceback"] = traceback_response
    return response, HTTPStatusCodes.INTERNAL_SERVER_ERROR


def get_json_wsgi_input(request, _response_on_exc):
    """Wraps the wsgi.input call in a try/except. The _response_on_exc function should be callable, and take one
    str param as for the traceback"""
    try:
        return json.loads(request.wsgi_environ["wsgi.input"].getvalue())
    except json.JSONDecodeError as exc:
        return _response_on_exc(repr(exc))


def valid_status_code(status_code):
    return status_code in [getattr(HTTPStatusCodes, k) for k in dir(HTTPStatusCodes) if not k.startswith("__")]


def web_response_wrapper(func, *args, **kwargs):
    """
    Wraps a function call in a try except so a HTTP status code is always returned.
    If the function returns a dictionary it is added to the response json.
    """
    status_code = HTTPStatusCodes.OK
    response = {"error": ErrorCodes.OK}
    try:
        if not callable(func):
            raise Exception("Implementation error: Must be callable.")

        res, status = func(*args, **kwargs)

        if isinstance(res, dict):
            response.update(**res)

        if valid_status_code(status):
            status_code = status

    except Exception as exc:
        response, status_code = internal_server_error(repr(exc))

    return (
        status_code,
        [("Content-type", "application/json; charset=utf-8")],
        [json.dumps(response).encode("UTF-8")]
    )
