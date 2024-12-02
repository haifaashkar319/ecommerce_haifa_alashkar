from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from sales.models import Sale, PurchaseHistory
from sales.routes import sales_bp

app = Flask(__name__)
init_db(app)
import sys
import os

# Add the current working directory to Python's module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Register Blueprint
app.register_blueprint(sales_bp)

if __name__ == "__main__":
    with app.app_context():
        tables = inspect(db.engine).get_table_names()
        print(f"DEBUG: Tables in database: {tables}")
        if 'sales' not in tables:
            print("Sales table not found. Creating tables...")
            db.create_all()
        else:
            print("Goods table already exists.")
        if 'purchase history' not in tables:
            print("Sales table not found. Creating tables...")
            db.create_all()
        else:
            print("Goods table already exists.")
    app.run(host="0.0.0.0", port=5003, debug=True)
