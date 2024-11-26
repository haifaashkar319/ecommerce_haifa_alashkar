import pytest
import random
import string
from database.db_config import db

def generate_unique_customer_username():
    """Generate a random unique username for a customer."""
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def generate_unique_good_name():
    """Generate a random unique name for a good."""
    return "good_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def test_create_customer(client):
    """Test creating a new customer."""
    customer_username = generate_unique_customer_username()
    response = client.post('/customer', json={
        "full_name": "Test Customer",
        "username": customer_username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201, f"Customer creation failed: {response.json}"
    assert response.json["message"] == "Customer created successfully"

def test_process_sale_success(client):
    """Test processing a successful sale."""
    # Add a customer
    customer_username = generate_unique_customer_username()
    client.post('/customer', json={
        "full_name": "Test Customer",
        "username": customer_username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    # Add wallet money for the customer
    with client.application.app_context():
        from customers.models import Customer
        customer = Customer.query.filter_by(username=customer_username).first()
        customer.wallet_balance = 100.0
        db.session.commit()

    # Add a good to the inventory
    good_name = generate_unique_good_name()
    add_response = client.post('/inventory/', json={
        "name": good_name,
        "category": "electronics",
        "price_per_item": 50.0,
        "description": "Electronic good.",
        "count_in_stock": 5
    })
    assert add_response.status_code == 201
    good_id = add_response.json["id"]

    # Process the sale
    sale_response = client.post('/sales/purchase', json={
        "customer_username": customer_username,
        "good_id": good_id,
        "quantity": 1
    })
    assert sale_response.status_code == 201, f"Sale processing failed: {sale_response.json}"
    sale_data = sale_response.json
    assert sale_data["customer_username"] == customer_username
    assert sale_data["good_id"] == good_id
    assert sale_data["quantity"] == 1

def test_process_sale_insufficient_wallet(client):
    """Test sale fails due to insufficient wallet balance."""
    # Add a customer with insufficient funds
    customer_username = generate_unique_customer_username()
    client.post('/customer', json={
        "full_name": "Test Customer",
        "username": customer_username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    # Add wallet money for the customer
    with client.application.app_context():
        from customers.models import Customer
        customer = Customer.query.filter_by(username=customer_username).first()
        customer.wallet_balance = 10.0
        db.session.commit()

    # Add a good to the inventory
    good_name = generate_unique_good_name()
    add_response = client.post('/inventory/', json={
        "name": good_name,
        "category": "electronics",
        "price_per_item": 50.0,
        "description": "Expensive good.",
        "count_in_stock": 5
    })
    assert add_response.status_code == 201
    good_id = add_response.json["id"]

    # Attempt to process the sale
    sale_response = client.post('/sales/purchase', json={
        "customer_username": customer_username,
        "good_id": good_id,
        "quantity": 1
    })
    assert sale_response.status_code == 400, f"Expected failure but got: {sale_response.json}"
    assert "Insufficient wallet balance" in sale_response.json["error"]

def test_process_sale_insufficient_stock(client):
    """Test sale fails due to insufficient stock."""
    # Add a customer with sufficient funds
    customer_username = generate_unique_customer_username()
    client.post('/customer', json={
        "full_name": "Test Customer",
        "username": customer_username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    # Add wallet money for the customer
    with client.application.app_context():
        from customers.models import Customer
        customer = Customer.query.filter_by(username=customer_username).first()
        customer.wallet_balance = 100.0
        db.session.commit()

    # Add a good with limited stock
    good_name = generate_unique_good_name()
    add_response = client.post('/inventory/', json={
        "name": good_name,
        "category": "electronics",
        "price_per_item": 10.0,
        "description": "Limited stock good.",
        "count_in_stock": 2
    })
    assert add_response.status_code == 201
    good_id = add_response.json["id"]

    # Attempt to process the sale with higher quantity
    sale_response = client.post('/sales/purchase', json={
        "customer_username": customer_username,
        "good_id": good_id,
        "quantity": 5  # Exceeds available stock
    })
    assert sale_response.status_code == 400, f"Expected failure but got: {sale_response.json}"
    assert "Good not available or insufficient stock" in sale_response.json["error"]
