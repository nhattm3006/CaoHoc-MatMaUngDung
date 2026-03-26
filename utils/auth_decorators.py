from flask import request, redirect, g, after_this_request
from functools import wraps
from utils.jwt_utils import decode_token, generate_access_token


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        payload = decode_token(access_token) if access_token else "MISSING"

        # Case 1: Valid access token
        if not isinstance(payload, str):
            g.user = payload
            return func(*args, **kwargs)

        # Case 2: Expired access token, try refresh
        if payload == "EXPIRED" and refresh_token:
            refresh_payload = decode_token(refresh_token)
            if not isinstance(refresh_payload, str) and refresh_payload.get("type") == "refresh":
                # Create new access token
                new_access_token = generate_access_token(
                    refresh_payload["user_id"], 
                    refresh_payload["username"], 
                    refresh_payload["role"]
                )
                
                @after_this_request
                def set_access_cookie(response):
                    response.set_cookie("access_token", new_access_token, httponly=True, samesite='Lax')
                    return response
                
                g.user = refresh_payload
                return func(*args, **kwargs)

        # Case 3: No valid tokens
        return redirect("/login")

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        payload = decode_token(access_token) if access_token else "MISSING"
        
        # If expired/missing, check refresh (similar to login_required)
        if isinstance(payload, str):
            if payload == "EXPIRED" and refresh_token:
                refresh_payload = decode_token(refresh_token)
                if not isinstance(refresh_payload, str) and refresh_payload.get("type") == "refresh":
                    new_access_token = generate_access_token(
                        refresh_payload["user_id"], 
                        refresh_payload["username"], 
                        refresh_payload["role"]
                    )
                    @after_this_request
                    def set_access_cookie(response):
                        response.set_cookie("access_token", new_access_token, httponly=True, samesite='Lax')
                        return response
                    payload = refresh_payload
                else:
                    return redirect("/login")
            else:
                return redirect("/login")

        if payload.get("role") != "admin":
            return redirect("/")

        g.user = payload
        return func(*args, **kwargs)

    return wrapper