from flask import Flask
from sqlalchemy import inspect
from database.db_config import init_db, db
from reviews.models import Review
from reviews.routes import reviews_bp
import sys
import os

# Add the current working directory to Python's module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__)
init_db(app)

# Register Blueprint
app.register_blueprint(reviews_bp)

if __name__ == "__main__":
    with app.app_context():
        tables = inspect(db.engine).get_table_names()
        print(f"DEBUG: Tables in database: {tables}")
        if 'review' not in tables:
            print("Review table not found. Creating tables...")
            db.create_all()
        else:
            print("Goods table already exists.")
    app.run(host="0.0.0.0", port=5004, debug=True)
