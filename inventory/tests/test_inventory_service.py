import pytest
import random
import string
import os
import sys

from profile_tests import profile_test 
from memory_tests import log_memory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from customers.models import Customer
from utils import create_token
from database.db_config import db

def generate_unique_item_name():
    """Generate a random unique item name for each test."""
    return "item_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_get_item(client):
    """Test retrieving a specific item by ID."""
    item_name = generate_unique_item_name()

    # Add an item to the inventory
    add_response = client.post('/inventory/', json={
        "name": item_name,
        "category": "accessories",
        "price_per_item": 15.99,
        "description": "A test accessory item.",
        "count_in_stock": 25
    })
    assert add_response.status_code == 201  # Ensure the item was added successfully
    item_id = add_response.json["id"]

    # Retrieve the item by ID
    response = client.get(f'/inventory/{item_id}')
    assert response.status_code == 200
    item = response.json
    assert item["name"] == item_name
    assert item["category"] == "accessories"
    assert item["price_per_item"] == 15.99
    assert item["count_in_stock"] == 25

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_get_all_items(client):
    """Test retrieving all items in the inventory."""
    item_name1 = generate_unique_item_name()
    item_name2 = generate_unique_item_name()

    # Add two items to the inventory
    response1 = client.post('/inventory/', json={
        "name": item_name1,
        "category": "food",
        "price_per_item": 5.99,
        "description": "A test food item.",
        "count_in_stock": 50
    })
    assert response1.status_code == 201

    response2 = client.post('/inventory/', json={
        "name": item_name2,
        "category": "clothes",
        "price_per_item": 19.99,
        "description": "A test clothing item.",
        "count_in_stock": 20
    })
    assert response2.status_code == 201

    # Retrieve all items
    response = client.get('/inventory/')
    assert response.status_code == 200
    items = response.json
    assert len(items) >= 2
    assert any(item["name"] == item_name1 for item in items)
    assert any(item["name"] == item_name2 for item in items)

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_get_item(client):
    """Test retrieving a specific item by ID."""
    item_name = generate_unique_item_name()

    # Add an item to the inventory
    add_response = client.post('/inventory/', json={
        "name": item_name,
        "category": "accessories",
        "price_per_item": 15.99,
        "description": "A test accessory item.",
        "count_in_stock": 25
    })
    item_id = add_response.json["id"]

    # Retrieve the item by ID
    response = client.get(f'/inventory/{item_id}')
    assert response.status_code == 200
    item = response.json
    assert item["name"] == item_name
    assert item["category"] == "accessories"
    assert item["price_per_item"] == 15.99
    assert item["count_in_stock"] == 25

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_update_item(client):
    """Test updating an item in the inventory."""
    item_name = generate_unique_item_name()

    # Add an item to the inventory
    add_response = client.post('/inventory/', json={
        "name": item_name,
        "category": "electronics",
        "price_per_item": 199.99,
        "description": "A test electronic item.",
        "count_in_stock": 5
    })
    item_id = add_response.json["id"]

    # Update the item
    response = client.put(f'/inventory/{item_id}', json={
        "price_per_item": 149.99,
        "description": "Updated electronic item.",
        "count_in_stock": 10
    })
    assert response.status_code == 200
    updated_item = response.json
    assert updated_item["price_per_item"] == 149.99
    assert updated_item["description"] == "Updated electronic item."
    assert updated_item["count_in_stock"] == 10

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_deduct_item(client):
    """Test deducting stock of an item."""
    item_name = generate_unique_item_name()

    # Add an item to the inventory
    add_response = client.post('/inventory/', json={
        "name": item_name,
        "category": "food",
        "price_per_item": 2.99,
        "description": "A test food item.",
        "count_in_stock": 20
    })
    assert add_response.status_code == 201
    item_id = add_response.json["id"]

    # Deduct stock from the item
    response = client.post(f'/inventory/{item_id}/deduct', json={"quantity": 5})
    assert response.status_code == 200
    assert response.json["updated_stock"]["count_in_stock"] == 15  # Expected stock after deduction

def test_unauthorized_access(client):
    """Test access without an Authorization header."""
    response = client.post('/inventory/', json={
        "name": "unauthorized_item",
        "category": "misc",
        "price_per_item": 10.99,
        "description": "Unauthorized item",
        "count_in_stock": 1
    }, no_auth=True)  # Ensure no Authorization header is added
    assert response.status_code == 403
    assert response.json["error"] == "Authorization header missing or malformed"

def test_unauthorized_access_non_admin(client):
    """Test access with a non-admin user or no Authorization header."""
    # Add a regular user (non-admin)
    regular_user = Customer(
        full_name="Regular User",
        username="regular",
        password="password",
        age=25,
        role="user"
    )
    db.session.add(regular_user)
    db.session.commit()

    # Generate a regular user token
    regular_token = create_token(regular_user.id)

    # Use the regular user's token for authentication
    response = client.post('/inventory/', json={
        "name": "unauthorized_item",
        "category": "misc",
        "price_per_item": 10.99,
        "description": "Unauthorized item",
        "count_in_stock": 1
    }, headers={"Authorization": f"Bearer {regular_token}"})

    assert response.status_code == 403
    assert response.json["error"] == "Access forbidden: Admins only"
def test_deduct_item_insufficient_stock(client):
    """Test deducting more items than are available in stock."""
    # Adding an item to the inventory
    response = client.post('/inventory/', json={
        "name": "item_with_stock",
        "category": "misc",
        "price_per_item": 15.99,
        "description": "Item with limited stock",
        "count_in_stock": 5
    })
    assert response.status_code == 201  # Item added successfully

    # Trying to deduct more than available in stock
    response = client.post('/inventory/1/deduct', json={
        "quantity": 10  # Deducting more than 5 in stock
    })
    
    assert response.status_code == 400  # Bad request (insufficient stock)
    assert response.json["error"] == "Insufficient stock available"
