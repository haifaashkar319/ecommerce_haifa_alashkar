import pytest
import os
import sys

# Ensure the project's root directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database.db_config import db

@pytest.fixture
def client():
    """
    Flask test client for testing the app.

    Configures the app to use an in-memory SQLite database for testing and
    sets up and tears down the database between tests.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables for the tests
        yield client  # Provide the client to the tests
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up after tests
