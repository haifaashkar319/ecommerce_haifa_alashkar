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

@app.route('/customer/<username>', methods=['GET'])
def get_customer(username):
    customer = CustomerService.get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

if __name__ == "__main__":
    app.run(debug=True)
