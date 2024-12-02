from database.db_config import db
from datetime import datetime

class Sale(db.Model):
    """
    Represents a sale record.

    Attributes:
        id (int): The unique ID of the sale.
        good_id (int): The ID of the associated good. Links to :class:`inventory.models.Goods`. :no-index:
        customer_username (str): The username of the customer. Links to :class:`customers.models.Customer`. :no-index:
        quantity (int): The quantity of goods sold.
        total_price (float): The total price of the sale.
        sale_date (datetime): The date of the sale.
    """
    __tablename__ = 'sales'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    customer_username = db.Column(db.String(100), db.ForeignKey('customers.username'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        """
        Converts the Sale record to a dictionary.

        Returns:
            dict: A dictionary representation of the Sale record.
        """
        return {
            "id": self.id,
            "good_id": self.good_id,
            "customer_username": self.customer_username,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "sale_date": self.sale_date.isoformat(),
        }

class PurchaseHistory(db.Model):
    """
    Represents the historical purchases made by customers.

    Attributes:
        id (int): The unique ID of the purchase history record.
        customer_username (str): The username of the customer. Links to :class:`customers.models.Customer`. :no-index:
        good_name (str): The name of the purchased good.
        total_price (float): The total price of the purchase.
        purchase_date (datetime): The date of the purchase.
    """
    __tablename__ = 'purchase_history'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(100), db.ForeignKey('customers.username'), nullable=False)
    good_name = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Converts the PurchaseHistory record to a dictionary.

        Returns:
            dict: A dictionary representation of the PurchaseHistory record.
        """
        return {
            "id": self.id,
            "customer_username": self.customer_username,
            "good_name": self.good_name,
            "total_price": self.total_price,
            "purchase_date": self.purchase_date.isoformat(),
        }
