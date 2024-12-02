from database.db_config import db

class Goods(db.Model):
    """
    Database model representing goods in the inventory.

    Attributes:
        id (int): Primary key for the item.
        name (str): Name of the item.
        category (str): Category of the item (e.g., food, clothes, electronics).
        price_per_item (float): Price per item.
        description (str): Description of the item (optional).
        count_in_stock (int): Count of available items in stock.
    """
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # E.g., food, clothes, electronics
    price_per_item = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    count_in_stock = db.Column(db.Integer, nullable=False)

    def add_stock(self, quantity):
        """Increase the stock of the item."""
        self.count_in_stock += quantity

    def deduct_stock(self, quantity):
        """Decrease the stock of the item."""
        if quantity > self.count_in_stock:
            raise ValueError("Insufficient stock to deduct.")
        self.count_in_stock -= quantity

    def to_dict(self):
        """Convert a Goods object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price_per_item": self.price_per_item,
            "description": self.description,
            "count_in_stock": self.count_in_stock
        }