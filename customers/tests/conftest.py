import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from customers.app import app as customers_app
from database.db_config import db

@pytest.fixture
def client():
    """
    Flask test client with a temporary SQLite database for testing.
    """
    from flask import Flask
    from customers.routes import customers_blueprint

    # Create a new app instance for tests
    app = Flask(__name__)
    app.register_blueprint(customers_blueprint)

    # Initialize the test database
    from database.db_config import init_db
    init_db(app, database_uri='sqlite:///:memory:')  # Use in-memory SQLite DB

    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.session.remove()
        db.drop_all()
