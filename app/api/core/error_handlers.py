import logging

import jwt
from flask import jsonify
from sqlalchemy.exc import DataError
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from app import app
from app import exceptions


@app.errorhandler(jwt.exceptions.ExpiredSignatureError)
def jwt_error_handler(e):
    code = 401
    logging.info(e)
    return error_response(status_code=code, message=str(e))


@app.errorhandler(exceptions.UnhealthyNode)
def unhealthy_error_handler(e):
    code = 400
    logging.info(e)
    return error_response(status_code=code, message=str(e))


@app.errorhandler(exceptions.BadAPIUsage)
@app.errorhandler(exceptions.BadServiceUsage)
@app.errorhandler(exceptions.NotAuthorized)
@app.errorhandler(exceptions.ContentNotFound)
@app.errorhandler(exceptions.APIKeyExpired)
@app.errorhandler(DataError)
@app.errorhandler(exceptions.DoNotHaveAccess)
@app.errorhandler(exceptions.TooManyRequests)
@app.errorhandler(exceptions.EmailNotVerified)
@app.errorhandler(exceptions.UserRegistrationProhibited)
def value_error_handler(e):
    code = e.code if isinstance(e, HTTPException) else 400
    logging.info(e)
    return error_response(status_code=code, message=str(e))


@app.errorhandler(exceptions.NodeAlreadyAssociated)
def node_is_connected_error_handler(e):
    code = 403
    logging.info(e)
    return error_response(status_code=code, message=str(e))


def error_response(status_code, message=None):
    payload = {'ok': False, 'message': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response
