import os
import sys
import pytest


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database.db_config import db
from customers.models import Customer
from inventory.models import Goods
from utils import create_token
@pytest.fixture
def client():
    """
    Flask test client with a shared in-memory SQLite database for testing.
    """
    from sales.app import app as sales_app  # Import the sales app

    # Use the same SQLite database for tests
    sales_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Shared in-memory DB
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    app = sales_app

    with app.app_context():
        # Recreate the database schema
        db.create_all()

        yield app.test_client()

        # Cleanup after the tests
        db.session.remove()
        db.drop_all()
