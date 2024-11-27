from flask import Flask
from database.db_config import init_db, db
from inventory.models import Goods  # Import the Inventory model
from inventory.routes import inventory_bp  # Import the Inventory Blueprint
from sales.models import Sale, PurchaseHistory  # Import the Sales models
from sales.routes import sales_bp  # Import the Sales Blueprint
from customers.routes import customers_blueprint  # Import the Customers Blueprint
from customers.models import Customer  # Import the Customer model
from reviews.models import Review  # Import the Reviews model
from reviews.routes import reviews_bp  # Import the Reviews Blueprint

app = Flask(__name__)
init_db(app)

# Register Blueprints
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(customers_blueprint)
app.register_blueprint(reviews_bp)  # Register the Reviews Blueprint

if __name__ == "__main__":
    with app.app_context():
        # Ensure all tables are created, including Customer, Goods, Sales, PurchaseHistory, and Reviews
        db.create_all()
    app.run(debug=True)
