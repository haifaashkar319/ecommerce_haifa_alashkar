import pytest
import random
import string
from database.db_config import db
from customers.models import Customer
from memory_tests import log_memory
from profile_tests import profile_test
from utils import create_token
from inventory.models import Goods
from reviews.models import Review


def generate_unique_username():
    """Generate a random unique username for testing."""
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def generate_unique_good_name():
    """Generate a random unique product name."""
    return "testproduct_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@profile_test
@log_memory(output_file="reviews_api_memory_usage.log")
def test_submit_review(client):
    """Test submitting a review."""
    with client.application.app_context():
        # Add a customer directly to the database
        username = generate_unique_username()
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

        # Add a product directly to the database
        product_name = generate_unique_good_name()
        product = Goods(
            name=product_name,
            category="electronics",
            price_per_item=50.0,
            description="A test product.",
            count_in_stock=10
        )
        db.session.add(product)
        db.session.commit()

        # Generate a token for the customer
        from utils import create_token  # Assuming the token creation utility is available
        customer_token = create_token(customer.id)

        # Submit a review with the token
        response = client.post(
            '/reviews/', 
            json={
                "customer_username": username,
                "product_id": product.id,
                "rating": 5,
                "comment": "Excellent product!"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 201, f"Expected 201 but got {response.status_code}: {response.json}"
        review = response.json
        assert "id" in review
        assert review["customer_username"] == username
        assert review["product_id"] == product.id
        assert review["rating"] == 5
        assert review["comment"] == "Excellent product!"

@profile_test
@log_memory(output_file="reviews_api_memory_usage.log")
def test_update_review(client):
    """Test updating a review."""
    with client.application.app_context():
        # Add a customer and product
        username = generate_unique_username()
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

        product_name = generate_unique_good_name()
        product = Goods(
            name=product_name,
            category="electronics",
            price_per_item=50.0,
            description="A test product.",
            count_in_stock=10
        )
        db.session.add(product)
        db.session.commit()

        # Submit a review
        review = Review(
            customer_username=username,
            product_id=product.id,
            rating=5,
            comment="Excellent product!"
        )
        db.session.add(review)
        db.session.commit()

        # Update the review
        response = client.put(f'/reviews/{review.id}', json={
            "rating": 4,
            "comment": "Good product."
        })

        assert response.status_code == 200
        updated_review = response.json
        assert updated_review["id"] == review.id
        assert updated_review["rating"] == 4
        assert updated_review["comment"] == "Good product."

@profile_test
@log_memory(output_file="reviews_api_memory_usage.log")
def test_delete_review(client):
    """Test deleting a review."""
    with client.application.app_context():
        # Add a customer and product
        username = generate_unique_username()
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

        product_name = generate_unique_good_name()
        product = Goods(
            name=product_name,
            category="electronics",
            price_per_item=50.0,
            description="A test product.",
            count_in_stock=10
        )
        db.session.add(product)
        db.session.commit()

        # Submit a review
        review = Review(
            customer_username=username,
            product_id=product.id,
            rating=5,
            comment="Excellent product!"
        )
        db.session.add(review)
        db.session.commit()

        # Delete the review
        response = client.delete(f'/reviews/{review.id}')
        assert response.status_code == 200
        assert response.json["message"] == "Review deleted successfully"

@profile_test
@log_memory(output_file="reviews_api_memory_usage.log")
def test_get_product_reviews(client):
    """Test retrieving all reviews for a product."""
    with client.application.app_context():
        # Add a product
        product_name = generate_unique_good_name()
        product = Goods(
            name=product_name,
            category="electronics",
            price_per_item=50.0,
            description="A test product.",
            count_in_stock=10
        )
        db.session.add(product)

        # Add two customers
        username1 = generate_unique_username()
        customer1 = Customer(
            full_name="John Doe",
            username=username1,
            password="password",
            age=30,
            address="123 Main St",
            gender="Male",
            marital_status="Single",
        )
        username2 = generate_unique_username()
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

        # Submit reviews
        review1 = Review(
            customer_username=username1,
            product_id=product.id,
            rating=5,
            comment="Excellent product!"
        )
        review2 = Review(
            customer_username=username2,
            product_id=product.id,
            rating=4,
            comment="Good product!"
        )
        db.session.bulk_save_objects([review1, review2])
        db.session.commit()

        # Retrieve reviews for the product
        response = client.get(f'/reviews/product/{product.id}')
        assert response.status_code == 200
        reviews = response.json
        assert len(reviews) == 2
        assert any(r["customer_username"] == username1 for r in reviews)
        assert any(r["customer_username"] == username2 for r in reviews)

@profile_test
@log_memory(output_file="reviews_api_memory_usage.log")
def test_moderate_review(client):
    """Test moderating a review."""
    with client.application.app_context():
        # Add a customer to the database
        customer_username = "testuser_moderate"
        customer = Customer(
            full_name="Test Customer",
            username=customer_username,
            password="password",
            age=30,
            address="123 Test Address",
            gender="Male",
            marital_status="Single"
        )
        db.session.add(customer)

        # Add an admin user to the database
        admin_username = "admin_user"
        admin = Customer(
            full_name="Admin User",
            username=admin_username,
            password="adminpassword",
            age=35,
            address="Admin Address",
            gender="Male",
            marital_status="Single",
            role="admin"
        )
        db.session.add(admin)

        # Add a product to the database
        product = Goods(
            name="Test Product",
            category="electronics",
            price_per_item=99.99,
            description="A test product.",
            count_in_stock=10
        )
        db.session.add(product)
        db.session.commit()

        # Generate tokens
        customer_token = create_token(customer.id)
        admin_token = create_token(admin.id)

        # Submit a review as the customer
        review_response = client.post('/reviews/', json={
            "customer_username": customer_username,
            "product_id": product.id,
            "rating": 5,
            "comment": "Excellent product!"
        }, headers={"Authorization": f"Bearer {customer_token}"})

        assert review_response.status_code == 201
        review = review_response.json
        assert "id" in review  # Ensure the response includes an ID
        review_id = review["id"]

        # Rebind the product instance to the active session (to avoid DetachedInstanceError)
        product = Goods.query.get(product.id)

        # Moderate the review as the admin
        moderate_response = client.put(f'/reviews/{review_id}/moderate', json={
            "status": "approved"
        }, headers={"Authorization": f"Bearer {admin_token}"})

        assert moderate_response.status_code == 200
        moderated_review = moderate_response.json
        assert moderated_review["id"] == review_id  # Ensure the ID matches
        assert moderated_review["status"] == "approved"

