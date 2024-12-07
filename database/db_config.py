from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app, database_uri=None):
    """
    Initialize the database with an optional database URI.

    Args:
        app (Flask): The Flask app instance.
        database_uri (str, optional): The URI of the database to use.
    """
    if "sqlalchemy" not in app.extensions:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri or 'mysql+pymysql://root:Haifa319*@localhost:3307/ecommerce_db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        print(f"DEBUG: Database URI set to {app.config['SQLALCHEMY_DATABASE_URI']}")
