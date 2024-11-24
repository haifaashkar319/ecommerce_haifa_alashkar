from flask import Flask, request, jsonify
from customers.services import CustomerService
from customers.models import Customer
from database.db_config import init_db

app = Flask(__name__)
init_db(app)

@app.route('/customer', methods=['POST'])
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

@app.route('/customer/<username>', methods=['PUT'])
def update_customer(username):
    """
    Updates a customer's information.

    Args:
        username (str): The username of the customer to update.

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
    data = request.json
    success = CustomerService.update_customer(username, data)
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Customer updated successfully"})

@app.route('/customer/<username>', methods=['DELETE'])
def delete_customer(username):
    """
    Deletes a customer by username.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        Response (JSON): A success message or error if the customer is not found.
    """
    success = CustomerService.delete_customer(username)
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Customer deleted successfully"})

@app.route('/customer/<username>', methods=['GET'])
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

@app.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Fetches all customers in the database.

    Returns:
        Response (JSON): A list of all customer records.
    """
    customers = CustomerService.get_all_customers()
    return jsonify(customers)

@app.route('/customer/<username>/wallet/charge', methods=['POST'])
def charge_wallet(username):
    """
    Charges an amount to a customer's wallet.

    Args:
        username (str): The username of the customer to charge.

    Expects a JSON payload with:
    - amount (float): The amount to charge.

    Returns:
        Response (JSON): A success message or error if the customer is not found.
    """
    data = request.json
    success = CustomerService.charge_wallet(username, data['amount'])
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Wallet charged successfully"})

@app.route('/customer/<username>/wallet/deduct', methods=['POST'])
def deduct_wallet(username):
    """
    Deducts an amount from a customer's wallet.

    Args:
        username (str): The username of the customer.

    Expects a JSON payload with:
    - amount (float): The amount to deduct.

    Returns:
        Response (JSON): A success message or error if the customer is not found or has insufficient funds.
    """
    data = request.json
    success = CustomerService.deduct_wallet(username, data['amount'])
    if not success:
        return jsonify({"error": "Customer not found or insufficient funds"}), 400
    return jsonify({"message": "Wallet deducted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
