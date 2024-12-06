import pytest
import random
import string
from database.db_config import db
from customers.models import Customer
from inventory.models import Goods

def generate_unique_customer_username():
    """Generate a random unique username for a customer."""
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def generate_unique_good_name():
    """Generate a random unique name for a good."""
    return "good_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def test_process_sale_success(client):
    """Test processing a successful sale."""
    from utils import create_token

    # Add a customer directly in the database
    customer_username = generate_unique_customer_username()
    customer = Customer(
        full_name="Test Customer",
        username=customer_username,
        password="password",
        age=30,
        address="123 Test St",
        gender="Male",
        marital_status="Single",
        wallet_balance=100.0,  # Add sufficient balance
        role="customer"
    )
    db.session.add(customer)

    # Add a good directly in the database
    good_name = generate_unique_good_name()
    good = Goods(
        name=good_name,
        category="electronics",
        price_per_item=50.0,
        description="Electronic good.",
        count_in_stock=5  # Add sufficient stock
    )
    db.session.add(good)
    db.session.commit()

    # Generate a token for the customer
    customer_token = create_token(customer.id)

    # Process the sale
    sale_response = client.post(
        '/sales/purchase',
        json={"good_id": good.id, "quantity": 1},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    
    # Assertions for success
    assert sale_response.status_code == 201, f"Sale processing failed: {sale_response.json}"
    sale_data = sale_response.json
    assert sale_data["good_id"] == good.id
    assert sale_data["quantity"] == 1


def test_process_sale_insufficient_stock(client):
    """Test sale fails due to insufficient stock."""
    from utils import create_token

    # Add a customer with sufficient funds
    customer_username = generate_unique_customer_username()
    customer = Customer(
        full_name="Test Customer",
        username=customer_username,
        password="password",
        age=30,
        address="123 Test St",
        gender="Male",
        marital_status="Single",
        wallet_balance=100.0,  # Sufficient balance
        role="customer"
    )
    db.session.add(customer)

    # Add a good with limited stock
    good_name = generate_unique_good_name()
    good = Goods(
        name=good_name,
        category="electronics",
        price_per_item=10.0,
        description="Limited stock good.",
        count_in_stock=2  # Limited stock
    )
    db.session.add(good)
    db.session.commit()

    # Generate a token for the customer
    customer_token = create_token(customer.id)

    # Attempt to process the sale with higher quantity
    sale_response = client.post(
        '/sales/purchase',
        json={"good_id": good.id, "quantity": 5},  # Exceeds available stock
        headers={"Authorization": f"Bearer {customer_token}"}
    )

    # Assertions for failure
    assert sale_response.status_code == 400, f"Expected failure but got: {sale_response.json}"
    assert "Good not available or insufficient stock" in sale_response.json["error"]


def test_process_sale_insufficient_wallet(client):
    """Test sale fails due to insufficient wallet balance."""
    from utils import create_token

    # Add a customer with insufficient funds
    customer = Customer(
        full_name="Test Customer",
        username="testuser",
        password="password",
        age=30,
        address="123 Test St",
        gender="Male",
        marital_status="Single",
        wallet_balance=10.0,  # Insufficient balance
        role="customer"
    )
    db.session.add(customer)

    # Add a good directly in the database
    good = Goods(
        name="Expensive Good",
        category="electronics",
        price_per_item=50.0,
        description="An expensive good.",
        count_in_stock=5
    )
    db.session.add(good)
    db.session.commit()

    # Generate a token for the customer
    customer_token = create_token(customer.id)

    # Attempt to process the sale
    sale_response = client.post(
        '/sales/purchase',
        json={"good_id": good.id, "quantity": 1},
        headers={"Authorization": f"Bearer {customer_token}"}
    )

    # Verify the response
    assert sale_response.status_code == 400, f"Expected failure but got: {sale_response.json}"
    assert "Insufficient wallet balance" in sale_response.json["error"]

