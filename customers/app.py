from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from customers.routes import customers_blueprint
import sys
import os

# Add the current working directory to Python's module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
init_db(app)

# Register Blueprint
app.register_blueprint(customers_blueprint)

if __name__ == "__main__":
    with app.app_context():
        if not inspect(db.engine).get_table_names():
            print("No tables found. Creating tables...")
            db.create_all()
        else:
            print("Tables already exist. No action needed.")
    app.run(host="0.0.0.0", port=5001, debug=True)
