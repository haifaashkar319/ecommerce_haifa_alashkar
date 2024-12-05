import os
import sys
import pytest
from flask import Flask


# Add the project root directory to the Python path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from customers.app import app as customers_app
from database.db_config import db
@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database for testing.
    """
    customers_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    app = customers_app
    with app.app_context():
        db.create_all()
        print("DEBUG: Initial table state (empty expected):")
        log_table_entries()  # Log table entries at the start
        yield app.test_client()
        print("DEBUG: Final table state after test:")
        log_table_entries()  # Log table entries after test
        db.session.remove()
        db.drop_all()  # Drop all tables to clean up


def log_table_entries():
    """Log the entries in the customers table."""
    from customers.models import Customer
    try:
        entries = Customer.query.all()
        for entry in entries:
            print(f"DEBUG: Customer in table -> Username: {entry.username}, Full Name: {entry.full_name}")
    except Exception as e:
        print(f"DEBUG: Error logging table entries: {e}")
