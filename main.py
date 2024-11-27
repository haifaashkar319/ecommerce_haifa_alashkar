from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from inventory.models import Goods
from inventory.routes import inventory_bp
from sales.models import Sale, PurchaseHistory
from sales.routes import sales_bp
from customers.routes import customers_blueprint
from customers.models import Customer
from reviews.models import Review
from reviews.routes import reviews_bp

app = Flask(__name__)
init_db(app)

# Register Blueprints
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(customers_blueprint)
app.register_blueprint(reviews_bp)

if __name__ == "__main__":
    with app.app_context():
        # Ensure tables are created, but only if they don't already exist
        if not inspect(db.engine).get_table_names():
            print("No tables found. Creating tables...")
            db.create_all()
        else:
            print("Tables already exist. No action needed.")
    app.run(debug=True)
