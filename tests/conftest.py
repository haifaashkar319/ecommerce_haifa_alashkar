import pytest
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database.db_config import db
@pytest.fixture
def client():
    """
    Flask test client for testing the app without dropping tables.

    Configures the app to use the main database without deleting tables.
    """
    # Set environment variable to differentiate test runs

    # Use the same database URI as the main app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Haifa319*@localhost:3307/ecommerce_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            # Ensure tables are created for the tests, but no deletion after tests
            db.create_all()  # Create tables if they don't exist
        yield client  # Provide the test client to the tests
