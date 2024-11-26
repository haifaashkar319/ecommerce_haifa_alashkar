from database.db_config import db
from datetime import datetime

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    customer_username = db.Column(db.String(100), db.ForeignKey('customers.username'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "good_id": self.good_id,
            "customer_username": self.customer_username,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "sale_date": self.sale_date.isoformat(),
        }

class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_history'

    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(100), db.ForeignKey('customers.username'), nullable=False)
    good_name = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_username": self.customer_username,
            "good_name": self.good_name,
            "total_price": self.total_price,
            "purchase_date": self.purchase_date.isoformat(),
        }
