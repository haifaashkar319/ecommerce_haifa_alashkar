import pytest
import random
import string


def generate_unique_username():
    """Generate a random unique username for each test."""
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


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
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert response.json["message"] == "Customer created successfully"


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
        "marital_status": "Single"
    })

    response = client.get(f'/customer/{username}')
    assert response.status_code == 200
    assert response.json["username"] == username
    assert response.json["full_name"] == "Test User"


def test_charge_wallet(client):
    """Test charging a customer's wallet."""
    username = generate_unique_username()
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single",
        "wallet_ballance": 0.0
    })

    response = client.post(f'/customer/{username}/wallet/charge', json={"amount": 50.0})
    assert response.status_code == 200
    assert response.json["message"] == "Wallet charged successfully"

    get_response = client.get(f'/customer/{username}')
    assert get_response.status_code == 200
    assert get_response.json["wallet_balance"] == 50.0


def test_deduct_wallet(client):
    """Test deducting money from a customer's wallet."""
    username = generate_unique_username()
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    client.post(f'/customer/{username}/wallet/charge', json={"amount": 100.0})

    response = client.post(f'/customer/{username}/wallet/deduct', json={"amount": 40.0})
    assert response.status_code == 200
    assert response.json["message"] == "Wallet deducted successfully"

    get_response = client.get(f'/customer/{username}')
    assert get_response.status_code == 200
    assert get_response.json["wallet_balance"] == 60.0


def test_delete_customer(client):
    """Test deleting a customer."""
    username = generate_unique_username()
    client.post('/customer', json={
        "full_name": "Test User",
        "username": username,
        "password": "password",
        "age": 30,
        "address": "123 Test St",
        "gender": "Male",
        "marital_status": "Single"
    })

    response = client.delete(f'/customer/{username}')
    assert response.status_code == 200
    assert response.json["message"] == "Customer deleted successfully"

    get_response = client.get(f'/customer/{username}')
    assert get_response.status_code == 404
    assert get_response.json["error"] == "Customer not found"
