from flask import request, jsonify
from functools import wraps
import jwt_utils as jwt_utils

def require_auth_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
    # def wrapper():

        token = request.headers.get('Authorization')
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
        try:
            jwt_utils.decode_token(token)
        except jwt_utils.JwtError as e:
            return jsonify({"error": str(e)}), 401

        # return f()
        return f(*args, **kwargs)
    return wrapper

