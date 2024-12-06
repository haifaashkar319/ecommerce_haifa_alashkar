import jwt
import datetime  # Use Python's datetime module
from flask import request, jsonify

# Replace this with your actual secret key
SECRET_KEY = "your_secret_key"

def extract_auth_token(req):
    """
    Extracts the Authorization token from the request headers.
    """
    auth_header = req.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

def decode_token(token):
    try:
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]  # Assuming "sub" contains the user_id
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        raise

def create_token(user_id):
    """
    Creates a JWT token for a given user ID.
    """
    payload = {
        "sub": user_id,
        "iat": datetime.datetime.utcnow(),  # Use datetime module
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Use datetime module
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def save_token(event_name, token):
    """
    Saves a token for debugging or logging purposes.
    """
    print(f"{event_name}: {token}")

def validate_json_payload(req, required_fields):
    """
    Validates that the JSON payload in a request contains all required fields.
    """
    data = req.get_json()
    if not data:
        return False, {"error": "Invalid JSON payload."}

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, {"error": f"Missing required fields: {', '.join(missing_fields)}"}

    return True, data
