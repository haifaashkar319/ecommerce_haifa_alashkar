from flask import Flask
from database.db_config import init_db, db
from inventory.models import Goods  # Import the Inventory model
from inventory.routes import inventory_bp  # Import the Inventory Blueprint
from sales.models import Sale, PurchaseHistory  # Import the Sales models
from sales.routes import sales_bp  # Import the Sales Blueprint
from customers.routes import customers_blueprint  # Import the Sales Blueprint
from customers.models import Customer  # Import the Customer model

app = Flask(__name__)
init_db(app)

# Register Blueprints for inventory and sales
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(customers_blueprint)  # Add this line to register customers blueprint


if __name__ == "__main__":
    with app.app_context():
        # Ensure all tables are created, including Customer, Goods, Sales, and PurchaseHistory
        db.create_all()
    app.run(debug=True)
