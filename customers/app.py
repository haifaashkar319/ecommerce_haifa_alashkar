import sys
import os
from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from customers.routes import customers_blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)

# Configure the production database
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:Haifa319*@localhost:3307/ecommerce_db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
init_db(app)

# Register Blueprint
app.register_blueprint(customers_blueprint)

if __name__ == "__main__":
    with app.app_context():
        inspector = inspect(db.engine)
        print(f"DEBUG: Active database URI (Production): {app.config['SQLALCHEMY_DATABASE_URI']}")
        if "customers" not in inspector.get_table_names():
            print("Customers table not found. Creating tables...")
            db.create_all()
        else:
            print("Customers table already exists. No action needed.")
    app.run(host="0.0.0.0", port=5001, debug=True)
