import os
import sys
import pytest
import random
import string
from sqlalchemy.sql import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from flask import Flask
from reviews.routes import reviews_bp
from database.db_config import db
from customers.models import Customer
from inventory.models import Goods
from utils import create_token

def generate_unique_username():
    """Generate a unique username for customers."""
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def generate_unique_good_name():
    """Generate a unique product name."""
    return "testproduct_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database for testing reviews.
    """
    # Create a new app instance for tests
    app = Flask(__name__)
    app.register_blueprint(reviews_bp)

    # Initialize the test database
    from database.db_config import init_db
    init_db(app, database_uri='sqlite:///:memory:')  # Use in-memory SQLite DB

    app.config['TESTING'] = True

    with app.app_context():
        # Enable SQLite foreign keys
        db.session.execute(text("PRAGMA foreign_keys=ON;"))
        db.create_all()

        # Seed a customer
        customer = Customer(
            full_name="Default Test User",
            username=generate_unique_username(),
            password="password",
            age=25,
            address="123 Test St",
            gender="Male",
            marital_status="Single"
        )
        db.session.add(customer)

        # Seed a product
        product = Goods(
            name=generate_unique_good_name(),
            category="electronics",
            price_per_item=50.0,
            description="A default product for testing.",
            count_in_stock=10
        )
        db.session.add(product)
        db.session.commit()

        # Generate token for the customer
        customer_token = create_token(customer.id)

        # Helper function to add the Authorization header
        def add_auth_header(client_request):
            def wrapper(path, *args, **kwargs):
                no_auth = kwargs.pop("no_auth", False)
                headers = kwargs.pop("headers", {})
                if not no_auth and "Authorization" not in headers:
                    headers["Authorization"] = f"Bearer {customer_token}"
                kwargs["headers"] = headers
                return client_request(path, *args, **kwargs)

            return wrapper

        # Wrap the Flask client methods
        test_client = app.test_client()
        test_client.get = add_auth_header(test_client.get)
        test_client.post = add_auth_header(test_client.post)
        test_client.put = add_auth_header(test_client.put)
        test_client.delete = add_auth_header(test_client.delete)

        yield test_client

        # Cleanup after tests
        db.session.execute(text("PRAGMA foreign_keys=OFF;"))  # Disable foreign keys for cleanup
        db.drop_all()
        db.session.commit()
        db.session.remove()
