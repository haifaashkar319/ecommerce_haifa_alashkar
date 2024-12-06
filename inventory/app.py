from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from inventory.models import Goods
from inventory.routes import inventory_bp
import sys
import os

# Add the current working directory to Python's module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:Haifa319*@localhost:3307/ecommerce_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
init_db(app)


# Register Blueprint
app.register_blueprint(inventory_bp)

if __name__ == "__main__":
    with app.app_context():
        tables = inspect(db.engine).get_table_names()
        print(f"DEBUG: Tables in database: {tables}")
        if 'goods' not in tables:
            print("Goods table not found. Creating tables...")
            db.create_all()
        else:
            print("Goods table already exists.")

    app.run(host="0.0.0.0", port=5002, debug=True)
