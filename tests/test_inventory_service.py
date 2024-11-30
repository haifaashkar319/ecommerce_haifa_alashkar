import pytest
import random
import string
from profile_tests import profile_test 
from memory_tests import log_memory


def generate_unique_item_name():
    """Generate a random unique item name for each test."""
    return "item_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_add_item(client):
    """Test adding an item to the inventory."""
    item_name = generate_unique_item_name()
    response = client.post('/inventory/', json={
        "name": item_name,
        "category": "electronics",
        "price_per_item": 99.99,
        "description": "A test electronic item.",
        "count_in_stock": 10
    })
    assert response.status_code == 201
    assert "id" in response.json  # Check if ID is returned

@profile_test
@log_memory(output_file="inventory_api_memory_usage.log")
def test_get_all_items(client):
    """Test retrieving all items in the inventory."""
    item_name1 = generate_unique_item_name()
    item_name2 = generate_unique_item_name()

    # Add two items to the inventory
    client.post('/inventory/', json={
        "name": item_name1,
        "category": "food",
        "price_per_item": 5.99,
        "description": "A test food item.",
        "count_in_stock": 50
    })
    client.post('/inventory/', json={
        "name": item_name2,
        "category": "clothes",
        "price_per_item": 19.99,
        "description": "A test clothing item.",
        "count_in_stock": 20
    })

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
    response = client.delete(f'/inventory/{item_id}', json={"quantity": 5})
    assert response.status_code == 200
    assert response.json["count_in_stock"] == 15  # Expected stock after deduction


def test_deduct_item_insufficient_stock(client):
    """Test attempting to deduct more stock than available."""
    item_name = generate_unique_item_name()

    # Step 1: Add an item to the inventory
    add_response = client.post('/inventory/', json={
        "name": item_name,
        "category": "food",
        "price_per_item": 2.99,
        "description": "A test food item.",
        "count_in_stock": 10  # Limited stock
    })
    assert add_response.status_code == 201  # Ensure the item was added
    item_id = add_response.json["id"]

    # Step 2: Attempt to deduct more stock than available
    deduct_response = client.delete(f'/inventory/{item_id}', json={"quantity": 15})  # Exceeds stock
    assert deduct_response.status_code == 400  # Expect a 400 Bad Request
    assert deduct_response.json["error"] == "Error deducting goods: Insufficient stock to deduct."
