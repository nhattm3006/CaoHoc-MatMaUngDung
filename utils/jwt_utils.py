import jwt
import datetime
from flask import current_app

def generate_access_token(user_id, username, role):
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "type": "access",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.secret_key, algorithm="HS256")

def generate_refresh_token(user_id, username, role):
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.secret_key, algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return "EXPIRED"
    except jwt.InvalidTokenError:
        return "INVALID"
