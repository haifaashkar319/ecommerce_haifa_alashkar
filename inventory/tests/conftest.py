import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from flask import Flask
from inventory.routes import inventory_bp
from database.db_config import db
from inventory.models import Goods
from customers.models import Customer
from utils import create_token


@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database for testing inventory.
    """
    # Create a new app instance for tests
    app = Flask(__name__)
    app.register_blueprint(inventory_bp)

    # Initialize the test database
    from database.db_config import init_db
    init_db(app, database_uri='sqlite:///:memory:')  # Use in-memory SQLite DB

    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        # Seed admin user
        admin_user = Customer(
            full_name="Admin User",
            username="admin",
            password="password",
            age=30,
            role="admin"
        )
        db.session.add(admin_user)

      
        # Seed inventory items

        db.session.commit()

        # Generate tokens
        admin_token = create_token(admin_user.id)

        # Helper function to add the Authorization header
        def add_auth_header(client_request):
            def wrapper(path, *args, **kwargs):
                no_auth = kwargs.pop("no_auth", False)
                is_admin = kwargs.pop("is_admin", False)
                headers = kwargs.pop("headers", {})

                if not no_auth and "Authorization" not in headers:
                    token = admin_token 
                    headers["Authorization"] = f"Bearer {token}"
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

        # Cleanup
        db.session.rollback()
        db.session.remove()
        db.drop_all()
