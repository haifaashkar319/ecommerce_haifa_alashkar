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
    Registers a new customer.

    Expects a JSON payload with:
    - full_name (str): The full name of the customer.
    - username (str): Unique username for the customer.
    - password (str): Password for the customer.
    - age (int): Age of the customer.
    - address (str, optional): Address of the customer.
    - gender (str, optional): Gender of the customer.
    - marital_status (str, optional): Marital status of the customer.

    Returns:
        Response (JSON): A success message with a 201 status code.
    """
    data = request.json
    customer = Customer(
        full_name=data['full_name'],
        username=data['username'],
        password=data['password'],
        age=data['age'],
        address=data.get('address'),
        gender=data.get('gender'),
        marital_status=data.get('marital_status'),
    )
    CustomerService.save_to_db(customer)
    return jsonify({"message": "Customer created successfully"}), 201

@customers_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Verify user credentials
    customer = Customer.query.filter_by(username=username).first()
    if not customer or customer.password != password:
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate JWT
    token = create_token(customer.id)
    print(f"DEBUG: Generated token for customer ID {customer.id}: {token}")

    # Save token
    save_token("Created Token", token)

    return jsonify({"access_token": token}), 200


@customers_blueprint.route('/customer/<username>', methods=['PUT'])
def update_customer(username):
    """
    Updates a customer's information.

    Args:
        username (str): The username of the customer to update.

    Requires an Authorization token in the header to identify the user.

    Expects a JSON payload with any of the following fields:
    - full_name (str, optional)
    - password (str, optional)
    - age (int, optional)
    - address (str, optional)
    - gender (str, optional)
    - marital_status (str, optional)
    - wallet_balance (float, optional)

    Returns:
        Response (JSON): A success message or error if the customer is not found.
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
        customer = Customer.query.get(user_id)
        if not customer or customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        success = CustomerService.update_customer(username, data)
        if not success:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer updated successfully"})

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@customers_blueprint.route('/customer/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Deletes a customer by username.

    Args:
        username (str): The username of the customer to delete.

    Requires an Authorization token in the header to identify the user.

    Returns:
        Response (JSON): A success message or error if the customer is not found.
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
        customer = Customer.query.get(user_id)
        if not customer or customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        success = CustomerService.delete_customer(username)
        if not success:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer deleted successfully"})

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@customers_blueprint.route('/customer/<username>', methods=['GET'])
def get_customer(username):
    """
    Fetches customer details by username.

    Args:
        username (str): The username of the customer.

    Returns:
        Response (JSON): The customer's details or an error if not found.
    """
    customer = CustomerService.get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

@customers_blueprint.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Fetches all customers in the database.

    Returns:
        Response (JSON): A list of all customer records.
    """
    customers = CustomerService.get_all_customers()
    return jsonify(customers)

@customers_blueprint.route('/customer/<username>/wallet/charge', methods=['POST'])
def charge_wallet(username):
    """
    Charges an amount to a customer's wallet.

    Args:
        username (str): The username of the customer.

    Requires an Authorization token in the header to identify the user.

    Expects a JSON payload with:
    - amount (float): The amount to charge.

    Returns:
        Response (JSON): A success message or error if the customer is not found.
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
        customer = Customer.query.get(user_id)
        if not customer or customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        # Process wallet charge
        data = request.json
        if not data or "amount" not in data:
            return jsonify({"error": "Amount is required"}), 400

        success = CustomerService.charge_wallet(username, data['amount'])
        if not success:
            return jsonify({"error": "Customer not found"}), 404

        return jsonify({"message": "Wallet charged successfully"})

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@customers_blueprint.route('/customer/<username>/wallet/deduct', methods=['POST'])
def deduct_wallet(username):
    """
    Deducts an amount from a customer's wallet.

    Args:
        username (str): The username of the customer.

    Requires an Authorization token in the header to identify the user.

    Expects a JSON payload with:
    - amount (float): The amount to deduct.

    Returns:
        Response (JSON): A success message or error if the customer is not found or if insufficient funds.
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
        customer = Customer.query.get(user_id)
        if not customer or customer.username != username:
            return jsonify({"error": "Unauthorized"}), 403

        # Process wallet deduction
        data = request.json
        if not data or "amount" not in data:
            return jsonify({"error": "Amount is required"}), 400

        success = CustomerService.deduct_wallet(username, data['amount'])
        if not success:
            return jsonify({"error": "Customer not found or insufficient funds"}), 400

        return jsonify({"message": "Wallet deducted successfully"})

    return jsonify({"error": "Authorization header missing or malformed"}), 403
