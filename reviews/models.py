from database.db_config import db
from datetime import datetime

class Review(db.Model):
    """
    Represents a product review.

    Attributes:
        id (int): The unique ID of the review.
        customer_username (str): The username of the customer submitting the review.
        product_id (int): The ID of the product being reviewed.
        rating (int): The rating given to the product (1-5 scale).
        comment (str): The textual feedback from the customer.
        created_at (datetime): The timestamp when the review was created.
        updated_at (datetime): The timestamp when the review was last updated.
        status (str): The moderation status of the review ('approved', 'flagged', or 'pending').

    """
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_username = db.Column(db.String(100), db.ForeignKey('customers.username'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # New field


    def to_dict(self):
        """
        Converts the review to a dictionary for API responses.

        Returns:
            dict: A dictionary representation of the review.
        """
        return {
            "id": self.id,
            "customer_username": self.customer_username,
            "product_id": self.product_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status
        }
