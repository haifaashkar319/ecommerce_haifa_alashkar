from pytest_mock import mocker
import random
import string
from customers.models import Customer
from database.db_config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from customers.services import CustomerService
from profile_tests import profile_test 
from memory_tests import log_memory
import uuid

def generate_unique_username():
    return "testuser_" + uuid.uuid4().hex[:8]


def test_login_and_authorization(client):
    """Test login and retrieve token."""
    username = generate_unique_username()
    
    # Register a user first
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    # Login to get the token
    login_response = client.post('/login', json={
        "username": username,
        "password": "password"
    })

    assert login_response.status_code == 200
    token = login_response.json['access_token']
    assert token, "Token should be returned"

    return token


### ROUTE TESTS ###
@profile_test
@log_memory(output_file="customers_api_memory_usage.log")
def test_register_customer(client):
    """Test customer registration."""
    username = generate_unique_username()
    response = client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })
    assert response.status_code == 201
    assert response.json["message"] == "Customer created successfully"

@profile_test
@log_memory(output_file="customers_api_memory_usage.log")
def test_get_customer(client):
    """Test retrieving a customer by username."""
    username = generate_unique_username()
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
    })

    response = client.get(f'/customer/{username}')
    assert response.status_code == 200
    assert response.json["username"] == username
    assert response.json["full_name"] == "Test User"

@profile_test
@log_memory(output_file="customers_api_memory_usage.log")
def test_charge_wallet(client):
    """Test charging a customer's wallet."""
    username = generate_unique_username()

    # Create a customer with the role
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"  # Add role explicitly
    })

    # Log in and get the token
    token = test_login_and_authorization(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Charge wallet
    response = client.post(f'/customer/{username}/wallet/charge', json={"amount": 50.0}, headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Wallet charged successfully"

    # Verify wallet balance
    get_response = client.get(f'/customer/{username}')
    assert get_response.status_code == 200
    assert get_response.json["wallet_balance"] == 50.0

@profile_test
@log_memory(output_file="customers_api_memory_usage.log")
def test_deduct_wallet(client):
    """Test deducting money from a customer's wallet."""
    username = generate_unique_username()

    # Create a customer
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })

    # Log in and get the token
    token = test_login_and_authorization(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Charge wallet first
    client.post(f'/customer/{username}/wallet/charge', json={"amount": 100.0}, headers=headers)

    # Deduct wallet
    response = client.post(f'/customer/{username}/wallet/deduct', json={"amount": 50.0}, headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Wallet deducted successfully"

    # Verify wallet balance
    get_response = client.get(f'/customer/{username}')
    assert get_response.status_code == 200
    assert get_response.json["wallet_balance"] == 50.0

def test_register_customer_invalid_data(client):
    """Test customer registration with invalid data."""
    # Missing required field 'username'
    response = client.post('/customer', json={
        "full_name": "Test User",
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert "Missing fields: username" in response.json["message"]

    # Missing multiple fields
    response = client.post('/customer', json={
        "full_name": "Test User"
    })
    assert response.status_code == 400
    assert "Missing fields: username, password, age, address, gender, marital_status" in response.json["message"]

def test_charge_wallet_invalid_amount(client):
    """Test charging the wallet with invalid amounts."""
    username = generate_unique_username()

    # Create a customer
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })

    # Log in and get the token
    token = test_login_and_authorization(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Charge wallet with negative amount
    response = client.post(f'/customer/{username}/wallet/charge', json={"amount": -50.0}, headers=headers)
    assert response.status_code == 400
    assert "Amount cannot be negative" in response.json["message"]

def test_deduct_wallet_insufficient_balance(client):
    """Test deducting wallet when balance is insufficient."""
    username = generate_unique_username()

    # Create a customer
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })

    # Log in and get the token
    token = test_login_and_authorization(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to deduct without charging first
    response = client.post(f'/customer/{username}/wallet/deduct', json={"amount": 50.0}, headers=headers)
    assert response.status_code == 400
    assert "Insufficient balance" in response.json["message"]

def test_register_customer_xss(client):
    """Test for XSS vulnerabilities during registration."""
    username = "<script>alert('xss')</script>"
    response = client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "role": "customer"
    })
    assert response.status_code == 400  # Expecting rejection
    assert "Invalid username" in response.json["message"]

def test_login_sql_injection(client):
    """Test for SQL injection vulnerabilities during login."""
    malicious_username = "' OR '1'='1"
    response = client.post('/login', json={
        "username": malicious_username,
        "password": "password"
    })
    assert response.status_code == 400  # Should not allow login
    assert "Invalid credentials" in response.json["message"]