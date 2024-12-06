"""
Customer Routes
===============

This module defines the Flask routes for managing customer-related operations.

Blueprint:
----------
- customers_blueprint: Blueprint for customer-related APIs.

Routes:
-------
- POST `/customer`: Create a new customer.
- POST `/login`: Login a customer.
- PUT `/customer/<username>`: Update an existing customer's information.
- DELETE `/customer/<username>`: Delete a customer.
- GET `/customer/<username>`: Fetch a customer's details.
- GET `/customers`: Fetch all customers.
- POST `/customer/<username>/wallet/charge`: Charge an amount to a customer's wallet.
- POST `/customer/<username>/wallet/deduct`: Deduct an amount from a customer's wallet.
"""

from flask import Blueprint, request, jsonify
from customers.services import CustomerService
from customers.models import Customer
from utils import SECRET_KEY, create_token, extract_auth_token, decode_token, save_token
import jwt

# Create a Blueprint for customer routes
customers_blueprint = Blueprint('customers', __name__)

@customers_blueprint.route('/customer', methods=['POST'])
def create_customer():
    """
    Create a new customer.

    **Endpoint**: `/customer`

    **Method**: `POST`

    **Request Body**:
        - `full_name` (str): Full name of the customer (required).
        - `username` (str): Unique username for the customer (required).
        - `password` (str): Password for the customer (required).
        - `age` (int): Age of the customer (required).
        - `address` (str): Address of the customer (optional).
        - `gender` (str): Gender of the customer (optional).
        - `marital_status` (str): Marital status of the customer (optional).
        - `role` (str): Role of the customer, defaults to "customer" (optional).

    **Response**:
        - `201 Created`: If the customer is created successfully.
        - `400 Bad Request`: If validation fails or required fields are missing.
        - `500 Internal Server Error`: If an unexpected error occurs.
        """

    try:
        # Validate the payload first
        data = request.json

        # Input sanitization for malicious inputs
        if '<' in data.get('username', '') or '>' in data.get('username', ''):
            return {"message": "Invalid username"}, 400

        CustomerService.validate_customer_payload(data)

        # Proceed to create a customer object only after validation
        customer = Customer(
            full_name=data['full_name'],
            username=data['username'],
            password=data['password'],
            age=data['age'],
            address=data.get('address'),
            gender=data.get('gender'),
            marital_status=data.get('marital_status'),
            role=data.get('role', 'customer'),  # Default to 'customer'
        )

        # Save to the database
        CustomerService.save_to_db(customer)
        return jsonify({"message": "Customer created successfully"}), 201

    except ValueError as e:
        # Validation error
        return {"message": str(e)}, 400
    except KeyError as e:
        # Handle unexpected KeyErrors gracefully
        return {"message": f"Missing required field: {str(e)}"}, 400
    except Exception as e:
        # Catch-all for unexpected errors
        return {"message": "An error occurred. Please try again."}, 500

@customers_blueprint.route('/login', methods=['POST'])
def login():
    """
    Login a customer.

    **Endpoint**: `/login`

    **Method**: `POST`

    **Request Body**:
        - `username` (str): Username of the customer (required).
        - `password` (str): Password of the customer (required).

    **Response**:
        - `200 OK`: If login is successful, returns an access token.
        - `400 Bad Request`: If the request payload is invalid.
        - `401 Unauthorized`: If login fails due to incorrect credentials.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    try:
        data = request.json

        # Validate payload presence
        if not data or "username" not in data or "password" not in data:
            return jsonify({"error": "Username and password are required"}), 400

        # Input sanitization for SQL injection prevention
        if "'" in data["username"] or '"' in data["username"]:
            return jsonify({"message": "Invalid credentials"}), 400

        # Call the login service
        result = CustomerService.login_customer(data["username"], data["password"])
        
        if "error" in result:
            return jsonify(result), 401  # Unauthorized
        return jsonify(result), 200  # Success

    except Exception as e:
        # Catch-all for unexpected errors
        return {"message": "An error occurred. Please try again."}, 500

@customers_blueprint.route('/customer/<username>', methods=['PUT'])
def update_customer(username):
    """
    Update an existing customer's information.

    **Endpoint**: `/customer/<username>`

    **Method**: `PUT`

    **URL Parameters**:
        - `username` (str): The username of the customer to update.

    **Request Body**:
        - Any of the following fields can be included:
          - `full_name` (str): Full name of the customer (optional).
          - `password` (str): Password of the customer (optional).
          - `age` (int): Age of the customer (optional).
          - `address` (str): Address of the customer (optional).
          - `gender` (str): Gender of the customer (optional).
          - `marital_status` (str): Marital status of the customer (optional).
          - `wallet_balance` (float): Wallet balance of the customer (optional).
          - `role` (str): Role of the customer (optional).

    **Response**:
        - `200 OK`: If the customer's information is updated successfully.
        - `400 Bad Request`: If the request payload is invalid or the update fails.
        - `403 Forbidden`: If the user is unauthorized to perform this action.
        - `404 Not Found`: If the customer does not exist.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    # Extract the token from the Authorization header
    header = extract_auth_token(request)
    if not header:
        return jsonify({"error": "Authorization header missing or malformed"}), 403

    try:
        # Decode the token and extract the user ID (primary key)
        user_id = decode_token(header)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Unauthorized"}), 403

    # Verify user identity
    customer = Customer.query.filter_by(id=user_id).first()
    if not customer:
        print(f"DEBUG: Customer with ID {user_id} not found.")
        return jsonify({"error": "Customer not found"}), 404

    if customer.username != username:
        print(f"DEBUG: Username mismatch. Token belongs to {customer.username}, but {username} was requested.")
        return jsonify({"error": "Unauthorized"}), 403
    # Get the JSON payload and validate
    data = request.json
    if not data:
        print("DEBUG: Invalid or missing JSON payload.")
        return jsonify({"error": "Invalid JSON payload."}), 400

    print(f"DEBUG: Received payload: {data}")

    # Delegate the update operation to the service
    success = CustomerService.update_customer(username, data)
    if not success:
        print("DEBUG: Update failed for username:", username)
        return jsonify({"error": "Failed to update customer."}), 400

    print(f"DEBUG: Customer {username} updated successfully.")
    return jsonify({"message": "Customer updated successfully"}), 200

@customers_blueprint.route('/customer/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Delete a customer by username.

    **Endpoint**: `/customer/<username>`

    **Method**: `DELETE`

    **URL Parameters**:
        - `username` (str): The username of the customer to delete.

    **Response**:
        - `200 OK`: If the customer is deleted successfully.
        - `403 Forbidden`: If the user is unauthorized to perform this action.
        - `404 Not Found`: If the customer does not exist.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    # Extract the token from the Authorization header
    header = extract_auth_token(request)
    if not header:
        return jsonify({"error": "Authorization header missing or malformed"}), 403

    try:
        # Decode the token and extract the user ID (primary key)
        user_id = decode_token(header)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Unauthorized"}), 403

    # Verify user identity
    customer = Customer.query.filter_by(id=user_id).first()
    if not customer:
        print(f"DEBUG: Customer with ID {user_id} not found.")
        return jsonify({"error": "Customer not found"}), 404

    if customer.username != username:
        print(f"DEBUG: Username mismatch. Token belongs to {customer.username}, but {username} was requested.")
        return jsonify({"error": "Unauthorized"}), 403

    # Delegate deletion logic to the service
    success = CustomerService.delete_customer(username)
    if not success:
        return jsonify({"error": "Customer not found"}), 404

    print(f"DEBUG: Customer {username} deleted successfully.")
    return jsonify({"message": "Customer deleted successfully"}), 200

@customers_blueprint.route('/customer/<username>', methods=['GET'])
def get_customer(username):
    """
    Fetch customer details by username.

    **Endpoint**: `/customer/<username>`

    **Method**: `GET`

    **URL Parameters**:
        - `username` (str): The username of the customer.

    **Response**:
        - `200 OK`: If the customer's details are retrieved successfully.
        - `404 Not Found`: If the customer does not exist.
    """
    customer = CustomerService.get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

@customers_blueprint.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Fetch all customers in the database.

    **Endpoint**: `/customers`

    **Method**: `GET`

    **Response**:
        - `200 OK`: If the list of customers is retrieved successfully.
        - `403 Forbidden`: If the user is unauthorized to perform this action.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        # Verify admin role
        customer = Customer.query.get(user_id)
        if not customer or customer.role != "admin":
            return jsonify({"error": "Access forbidden: Admins only"}), 403

        customers = CustomerService.get_all_customers()
        return jsonify(customers)

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@customers_blueprint.route('/customer/<username>/wallet/charge', methods=['POST'])
def charge_wallet(username):
    """
    Charge an amount to a customer's wallet.

    **Endpoint**: `/customer/<username>/wallet/charge`

    **Method**: `POST`

    **URL Parameters**:
        - `username` (str): The username of the customer.

    **Request Body**:
        - `amount` (float): The amount to charge (required, must be non-negative).

    **Response**:
        - `200 OK`: If the wallet is charged successfully.
        - `400 Bad Request`: If the request payload is invalid or the amount is negative.
        - `403 Forbidden`: If the user is unauthorized to perform this action.
        - `404 Not Found`: If the customer does not exist.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    # Extract and validate token
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        # Verify user identity
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        if customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        # Process wallet charge
        data = request.json
        if not data or "amount" not in data:
            return jsonify({"error": "Amount is required"}), 400
        
        if data.get("amount") < 0:
            return jsonify({"message": "Amount cannot be negative"}), 400

        success = CustomerService.charge_wallet(username, data['amount'])
        if not success:
            return jsonify({"error": "Error updating wallet balance"}), 500

        return jsonify({"message": "Wallet charged successfully"}), 200

    return jsonify({"error": "Authorization header missing or malformed"}), 403
@customers_blueprint.route('/customer/<username>/wallet/deduct', methods=['POST'])
def deduct_wallet(username):
    """
    Deduct an amount from a customer's wallet.

    **Endpoint**: `/customer/<username>/wallet/deduct`

    **Method**: `POST`

    **URL Parameters**:
        - `username` (str): The username of the customer.

    **Request Body**:
        - `amount` (float): The amount to deduct (required, must not exceed wallet balance).

    **Response**:
        - `200 OK`: If the amount is deducted successfully.
        - `400 Bad Request`: If the request payload is invalid or there is insufficient balance.
        - `403 Forbidden`: If the user is unauthorized to perform this action.
        - `404 Not Found`: If the customer does not exist.
        - `500 Internal Server Error`: If an unexpected error occurs.
    """
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        # Verify user identity
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        if customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        # Process wallet charge
        data = request.json
        if not data or "amount" not in data:
            return jsonify({"error": "Amount is required"}), 400

        if data.get("amount") > customer.wallet_balance:
            return jsonify({"message": "Insufficient balance"}), 400

        success = CustomerService.deduct_wallet(username, data['amount'])
        if not success:
            return jsonify({"error": "Error updating wallet balance"}), 500

        return jsonify({"message": "Wallet deducted successfully"}), 200

    return jsonify({"error": "Authorization header missing or malformed"}), 403

