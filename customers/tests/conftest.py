import os
import sys
from flask import Flask
from customers.routes import customers_blueprint
from database.db_config import db, init_db
import pytest
from customers.app import app as customers_app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database.
    """
    app = customers_app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Temporary in-memory database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
