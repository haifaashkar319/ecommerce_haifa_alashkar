from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Haifa319*@localhost:3307/ecommerce_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
