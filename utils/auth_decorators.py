from flask import request, redirect, g, after_this_request
from functools import wraps
from utils.jwt_utils import decode_token, generate_access_token, generate_refresh_token


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        payload = decode_token(access_token) if access_token else "MISSING"

        # Case 1: Valid access token (Must be type 'access')
        if not isinstance(payload, str) and payload.get("type") == "access":
            g.user = payload
            return func(*args, **kwargs)

        # Case 2: Expired access token, try refresh
        if (payload == "EXPIRED" or (not isinstance(payload, str) and payload.get("type") != "access")) and refresh_token:
            refresh_payload = decode_token(refresh_token)
            if not isinstance(refresh_payload, str) and refresh_payload.get("type") == "refresh":
                # Create NEW access token AND NEW refresh token (Rotation)
                new_access = generate_access_token(
                    refresh_payload["user_id"], 
                    refresh_payload["username"], 
                    refresh_payload["role"]
                )
                new_refresh = generate_refresh_token(
                    refresh_payload["user_id"], 
                    refresh_payload["username"], 
                    refresh_payload["role"]
                )
                
                @after_this_request
                def set_tokens_cookie(response):
                    response.set_cookie("access_token", new_access, httponly=True, samesite='Lax', max_age=3600)
                    response.set_cookie("refresh_token", new_refresh, httponly=True, samesite='Lax', max_age=3600)
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
        
        # If invalid/expired, try refresh
        if isinstance(payload, str) or payload.get("type") != "access":
            if (payload == "EXPIRED" or (not isinstance(payload, str) and payload.get("type") != "access")) and refresh_token:
                refresh_payload = decode_token(refresh_token)
                if not isinstance(refresh_payload, str) and refresh_payload.get("type") == "refresh":
                    # Rotation for Admin too
                    new_access = generate_access_token(
                        refresh_payload["user_id"], 
                        refresh_payload["username"], 
                        refresh_payload["role"]
                    )
                    new_refresh = generate_refresh_token(
                        refresh_payload["user_id"], 
                        refresh_payload["username"], 
                        refresh_payload["role"]
                    )
                    @after_this_request
                    def set_tokens_cookie(response):
                        response.set_cookie("access_token", new_access, httponly=True, samesite='Lax', max_age=3600)
                        response.set_cookie("refresh_token", new_refresh, httponly=True, samesite='Lax', max_age=3600)
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