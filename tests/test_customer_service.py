import pytest
import random
import string
from customers.models import Customer
from database.db_config import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from unittest.mock import patch, MagicMock
from customers.services import CustomerService


def generate_unique_username():
    """Generate a random unique username for each test."""
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


### ROUTE TESTS ###
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
        "marital_status": "Single"
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


### MODEL TESTS ###
def test_customer_model_charge_wallet(client):
    """Test the charge_wallet static method in the Customer model."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=0.0
        )
        db.session.add(customer)
        db.session.commit()

        success = Customer.charge_wallet(username=username, amount=50.0)
        assert success, "charge_wallet method failed"

        updated_customer = Customer.query.filter_by(username=username).first()
        assert updated_customer.wallet_balance == 50.0


def test_customer_model_deduct_wallet(client):
    """Test the deduct_wallet static method in the Customer model."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=100.0
        )
        db.session.add(customer)
        db.session.commit()

        success = Customer.deduct_wallet(username=username, amount=40.0)
        assert success, "deduct_wallet method failed"

        updated_customer = Customer.query.filter_by(username=username).first()
        assert updated_customer.wallet_balance == 60.0

        insufficient_funds = Customer.deduct_wallet(username=username, amount=100.0)
        assert not insufficient_funds, "deduct_wallet should fail with insufficient funds"

        updated_customer = Customer.query.filter_by(username=username).first()
        assert updated_customer.wallet_balance == 60.0


def test_customer_to_dict(client):
    """Test the to_dict method in the Customer model."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=100.0,
            address="123 Test St",
            gender="Male",
            marital_status="Single"
        )
        db.session.add(customer)
        db.session.commit()

        customer_dict = customer.to_dict()
        assert customer_dict["full_name"] == "Test User"
        assert customer_dict["username"] == username
        assert customer_dict["wallet_balance"] == 100.0
        assert customer_dict["address"] == "123 Test St"
        assert customer_dict["gender"] == "Male"
        assert customer_dict["marital_status"] == "Single"


### EXCEPTION HANDLING TESTS ###
def test_charge_wallet_exception(client, mocker):
    """Test exception handling in the charge_wallet method."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=0.0
        )
        db.session.add(customer)
        db.session.commit()

        mocker.patch("customers.models.db.session.execute", side_effect=SQLAlchemyError("Database error"))
        success = Customer.charge_wallet(username=username, amount=50.0)
        assert not success


def test_deduct_wallet_exception(client, mocker):
    """Test exception handling in the deduct_wallet method."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=100.0
        )
        db.session.add(customer)
        db.session.commit()

        mocker.patch("customers.models.db.session.execute", side_effect=SQLAlchemyError("Database error"))
        success = Customer.deduct_wallet(username=username, amount=50.0)
        assert not success

def test_charge_wallet_exception_handling(client, mocker):
    """Test exception handling in the charge_wallet method."""
    username = generate_unique_username()
    with client.application.app_context():
        from customers.models import Customer
        from customers.services import CustomerService

        # Create a new customer
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=100.0
        )
        db.session.add(customer)
        db.session.commit()

        # Mock the database operation to raise an exception
        mocker.patch("customers.services.db.session.execute", side_effect=SQLAlchemyError("Mocked SQL error"))

        # Call the service and ensure exception is handled
        success = CustomerService.charge_wallet(username, 50.0)
        assert not success, "charge_wallet should return False on exception"

        # Verify wallet balance is unchanged
        updated_customer = Customer.query.filter_by(username=username).first()
        assert updated_customer.wallet_balance == 100.0, "Wallet balance should remain unchanged after exception"


def test_deduct_wallet_exception_handling(client, mocker):
    """Test exception handling in the deduct_wallet method."""
    username = generate_unique_username()
    with client.application.app_context():
        from customers.models import Customer
        from customers.services import CustomerService

        # Create a new customer
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            wallet_balance=200.0
        )
        db.session.add(customer)
        db.session.commit()

        # Mock the database operation to raise an exception
        mocker.patch("customers.services.db.session.execute", side_effect=SQLAlchemyError("Mocked SQL error"))

        # Call the service and ensure exception is handled
        success = CustomerService.deduct_wallet(username, 50.0)
        assert not success, "deduct_wallet should return False on exception"

        # Verify wallet balance is unchanged
        updated_customer = Customer.query.filter_by(username=username).first()
        assert updated_customer.wallet_balance == 200.0, "Wallet balance should remain unchanged after exception"
        
