from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime

def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            os.getenv('SUPABASE_JWT_SECRET'),
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.user_id = payload.get('sub')
        request.user_email = payload.get('email')
        
        return f(*args, **kwargs)
    
    return decorated 