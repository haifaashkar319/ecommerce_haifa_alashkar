from flask import Flask, request, jsonify
from customers.services import CustomerService
from customers.models import Customer
from database.db_config import init_db, db

app = Flask(__name__)
init_db(app)

@app.route('/customer', methods=['POST'])
def create_customer():
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
    data = request.json
    success = CustomerService.update_customer(username, data)
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Customer updated successfully"})

@app.route('/customer/<username>', methods=['DELETE'])
def delete_customer(username):
    success = CustomerService.delete_customer(username)
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Customer deleted successfully"})

@app.route('/customer/<username>', methods=['GET'])
def get_customer(username):
    customer = CustomerService.get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = CustomerService.get_all_customers()
    return jsonify(customers)

@app.route('/customer/<username>/wallet/charge', methods=['POST'])
def charge_wallet(username):
    data = request.json
    success = CustomerService.charge_wallet(username, data['amount'])
    if not success:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"message": "Wallet charged successfully"})

@app.route('/customer/<username>/wallet/deduct', methods=['POST'])
def deduct_wallet(username):
    data = request.json
    success = CustomerService.deduct_wallet(username, data['amount'])
    if not success:
        return jsonify({"error": "Customer not found or insufficient funds"}), 400
    return jsonify({"message": "Wallet deducted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
