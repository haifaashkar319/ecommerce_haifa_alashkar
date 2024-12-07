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
    print(f"Authorization Header: {auth_header}")  # Debugging statement
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        print(f"Extracted Token: {token}")  # Debugging statement
        return token
    print("Authorization header missing or malformed")  # Debugging statement
    return None

def decode_token(token):
    try:
        # print(f"Raw Token: {token}")
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]
        # print(f"Token after removing Bearer prefix: {token}")

        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # print(f"Decoded Token Payload: {payload}")

        # Ensure the 'sub' field exists
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token: Subject (sub) not found in token payload")

        return str(user_id)  # Always return user_id as a string
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
    try:
        # print(f"Creating token for user ID: {user_id}")
        payload = {
            "sub": str(user_id),  # Explicitly cast user_id to a string
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        # print(f"Payload before encoding: {payload}")
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        # print(f"Generated Token: {token}")
        return token
    except Exception as e:
        print(f"Error creating token: {e}")
        raise

def save_token(event_name, token):
    """
    Saves a token for debugging or logging purposes.
    """
    print(f"{event_name}: {token}")  # Debugging statement for token saving

def validate_json_payload(req, required_fields):
    """
    Validates that the JSON payload in a request contains all required fields.
    """
    try:
        print("Validating JSON payload...")  # Debugging statement
        data = req.get_json()
        print(f"Received Payload: {data}")  # Debugging statement
        if not data:
            print("Invalid JSON payload.")  # Debugging statement
            return False, {"error": "Invalid JSON payload."}

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"Missing required fields: {missing_fields}")  # Debugging statement
            return False, {"error": f"Missing required fields: {', '.join(missing_fields)}"}

        print("Payload validation successful.")  # Debugging statement
        return True, data
    except Exception as e:
        print(f"Error validating JSON payload: {e}")  # Debugging statement
        raise
