from flask import Flask
from database.db_config import init_db, db
from inventory.models import Goods  # Import the model
from inventory.routes import inventory_bp  # Import the Blueprint

app = Flask(__name__)
init_db(app)

# Register the Blueprint for inventory
app.register_blueprint(inventory_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables, including the Goods table
    app.run(debug=True)
