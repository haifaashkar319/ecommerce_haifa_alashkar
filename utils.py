from datetime import datetime, timedelta
import jwt

SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"  # Replace with your actual secret key

TOKEN_FILE = "saved_tokens.txt"

def save_token(label, token):
    with open(TOKEN_FILE, "a") as file:
        file.write(f"{label}: {token}\n")
    print(f"DEBUG: {label} saved: {token}")

def create_token(user_id):
    print(f"DEBUG: Creating token for user ID: {user_id}")
    payload = {
        'exp': datetime.utcnow() + timedelta(days=60),  # Token expiration
        'iat': datetime.utcnow(),  # Issued at
        'sub': str(user_id)  # Subject (user ID as a string)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(f"DEBUG: Token created: {token}")
    return token


def extract_auth_token(authenticated_request):
    print("DEBUG: Extracting Authorization token from request headers")
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        print(f"DEBUG: Authorization header found: {auth_header}")
        return auth_header.split(" ")[1]  # Bearer <token>
    print("DEBUG: Authorization header missing")
    return None


def decode_token(token):
    print(f"DEBUG: Decoding token: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(f"DEBUG: Decoded payload: {payload}")
        return int(payload['sub'])  # Convert back to integer for application logic
    except jwt.ExpiredSignatureError:
        print("DEBUG: Token has expired")
        raise
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Invalid token. Error: {str(e)}")
        raise


