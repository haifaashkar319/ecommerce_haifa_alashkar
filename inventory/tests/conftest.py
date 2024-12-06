import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.db_config import db  # Import the db object
from customers.models import Customer
from utils import create_token

@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database for testing the inventory.
    """
    from inventory.app import app as inventory_app

    inventory_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    app = inventory_app

    with app.app_context():
        db.create_all()

        # Create an admin user
        admin_user = Customer(
            full_name="Admin User",
            username="admin",
            password="password",
            age=30,
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()

        # Generate an admin token
        admin_token = create_token(admin_user.id)

        # Helper function to add the Authorization header
        def add_auth_header(client_request):
            def wrapper(path, *args, **kwargs):
                # Handle no_auth manually
                no_auth = kwargs.pop("no_auth", False)
                headers = kwargs.pop("headers", {})
                if not no_auth and "Authorization" not in headers:
                    headers["Authorization"] = f"Bearer {admin_token}"
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

        db.session.remove()
        db.drop_all()
