from functools import wraps
import traceback

from flask import Flask, request, jsonify, current_app

import jwt

# Dummy User class, usually this would be Database ORMs.
# For this interview exercise a dummy class will do fine.
class User(object):
    id = None
    public_id = None
    name = None
    email = None
    password = None

# Decorator for verifying the JWT token for authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        # return 401 if token is not passed
        if not token:
            return jsonify({"message" : "JWT Token is required!!"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, current_app.config["SECRET_KEY"])


            # Normally this is where we would get the user from database,
            # but for this exercise, a dummy User is created with hardcoded
            # id to match the passed in JWT token

            # current_user = User.query\
            #     .filter_by(public_id = data["public_id"])\
            #     .first()

            current_user = User()
            current_user.public_id = "123456789"

        except:
            return jsonify({
                "message" : "Token is invalid !!"
            }), 401

        # For now return nothing, but we could also return the logged in user
        return f(*args, **kwargs)

    return decorated