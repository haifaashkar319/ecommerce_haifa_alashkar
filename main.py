"""
Main Application Entry Point
============================

This module initializes the Flask application, sets up the database, and registers blueprints.

Modules:
--------
- `customers.routes`: Contains customer-related API routes.

Usage:
------
Run this file to start the Flask application.
"""

from flask import Flask
from customers.routes import customers_blueprint
from database.db_config import init_db

app = Flask(__name__)
init_db(app)

# Register the blueprint for customer routes
app.register_blueprint(customers_blueprint, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)
