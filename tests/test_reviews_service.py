import pytest
import random
import string
from database.db_config import db
from customers.models import Customer


def generate_unique_username():
    """Generate a random unique username for testing."""
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


@pytest.fixture
def setup_customer(client):
    """Set up a default customer for testing."""
    username = generate_unique_username()
    with client.application.app_context():
        customer = Customer(
            full_name="Test User",
            username=username,
            password="password",
            age=30,
            address="123 Main St",
            gender="Male",
            marital_status="Single",
        )
        db.session.add(customer)
        db.session.commit()
    return username


def test_submit_review(client, setup_customer):
    """Test submitting a review."""
    username = setup_customer

    # Submit a new review
    response = client.post('/reviews/', json={
        "customer_username": username,
        "product_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert response.status_code == 201
    review = response.json
    assert "id" in review  # Ensure the response includes an ID
    assert review["id"] > 0  # ID should be a valid positive integer
    assert review["customer_username"] == username
    assert review["product_id"] == 1
    assert review["rating"] == 5
    assert review["comment"] == "Excellent product!"


def test_update_review(client, setup_customer):
    """Test updating a review."""
    username = setup_customer

    # Submit a review first
    review_response = client.post('/reviews/', json={
        "customer_username": username,
        "product_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert review_response.status_code == 201
    review = review_response.json
    assert "id" in review  # Ensure the response includes an ID
    review_id = review["id"]

    # Update the review
    update_response = client.put(f'/reviews/{review_id}', json={
        "rating": 4,
        "comment": "Good product."
    })
    assert update_response.status_code == 200
    updated_review = update_response.json
    assert updated_review["id"] == review_id  # Ensure the ID remains the same
    assert updated_review["rating"] == 4
    assert updated_review["comment"] == "Good product."


def test_delete_review(client, setup_customer):
    """Test deleting a review."""
    username = setup_customer

    # Submit a review first
    review_response = client.post('/reviews/', json={
        "customer_username": username,
        "product_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert review_response.status_code == 201
    review = review_response.json
    assert "id" in review  # Ensure the response includes an ID
    review_id = review["id"]

    # Delete the review
    delete_response = client.delete(f'/reviews/{review_id}')
    assert delete_response.status_code == 200
    assert delete_response.json["message"] == "Review deleted successfully"


def test_get_product_reviews(client):
    """Test retrieving all reviews for a product."""
    product_id = 1
    username1 = generate_unique_username()
    username2 = generate_unique_username()

    with client.application.app_context():
        from reviews.models import Review
        from database.db_config import db
        # Get the initial count of reviews for the product
        initial_count = db.session.query(Review).filter_by(product_id=product_id).count()

        # Add two customers for the test
        from customers.models import Customer
        customer1 = Customer(
            full_name="John Doe",
            username=username1,
            password="password",
            age=30,
            address="123 Main St",
            gender="Male",
            marital_status="Single",
        )
        customer2 = Customer(
            full_name="Jane Doe",
            username=username2,
            password="password",
            age=28,
            address="456 Main St",
            gender="Female",
            marital_status="Single",
        )
        db.session.bulk_save_objects([customer1, customer2])
        db.session.commit()

    # Submit two reviews for the same product
    response_1 = client.post('/reviews/', json={
        "customer_username": username1,
        "product_id": product_id,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert response_1.status_code == 201

    response_2 = client.post('/reviews/', json={
        "customer_username": username2,
        "product_id": product_id,
        "rating": 4,
        "comment": "Good product!"
    })
    assert response_2.status_code == 201

    # Retrieve reviews for the product
    response = client.get(f'/reviews/product/{product_id}')
    assert response.status_code == 200
    reviews = response.json

    # Calculate the expected total count
    expected_count = initial_count + 2
    assert len(reviews) == expected_count, f"Expected {expected_count} reviews, got {len(reviews)}"
    assert any(review["customer_username"] == username1 for review in reviews)
    assert any(review["customer_username"] == username2 for review in reviews)


def test_moderate_review(client, setup_customer):
    """Test moderating a review."""
    username = setup_customer

    # Submit a review first
    review_response = client.post('/reviews/', json={
        "customer_username": username,
        "product_id": 1,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert review_response.status_code == 201
    review = review_response.json
    assert "id" in review  # Ensure the response includes an ID
    review_id = review["id"]

    # Moderate the review
    moderate_response = client.put(f'/reviews/{review_id}/moderate', json={
        "status": "approved"
    })
    assert moderate_response.status_code == 200
    moderated_review = moderate_response.json
    assert moderated_review["id"] == review_id  # Ensure the ID matches
    assert moderated_review["status"] == "approved"
