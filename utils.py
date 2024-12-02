from datetime import datetime, timedelta
import jwt

# Shared secret key
SECRET_KEY = "your-secret-key"  # Replace with your secure key

# Save token to file
def save_token(label, token):
    with open("saved_tokens.txt", "a") as file:
        file.write(f"{label}: {token}\n")

# Extract Authorization token
def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get("Authorization")
    if auth_header:
        return auth_header.split(" ")[1]  # Bearer <token>
    return None

# Decode JWT
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]  # Return the subject (user ID)
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")
