from database.db_config import db
from sqlalchemy.sql import text  


class Customer(db.Model):
    """
    Represents a customer in the system.

    Attributes:
        id (int): The primary key of the customer record.
        full_name (str): The full name of the customer.
        username (str): The unique username of the customer.
        password (str): The password for the customer (hashed).
        age (int): The age of the customer.
        address (str, optional): The address of the customer.
        gender (str, optional): The gender of the customer.
        marital_status (str, optional): The marital status of the customer.
        wallet_balance (float): The wallet balance of the customer.
    """
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    wallet_balance = db.Column(db.Float, default=0.0)

    @staticmethod
    def charge_wallet(username, amount):
        """
        Charges a specified amount to a customer's wallet.
        """
        try:
            query = text("""
                UPDATE customers
                SET wallet_balance = wallet_balance + :amount
                WHERE username = :username
            """)
            result = db.session.execute(query, {"amount": amount, "username": username})
            db.session.commit()
            return result.rowcount > 0
        except Exception as e:
            print(f"Error in charge_wallet: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def deduct_wallet(username, amount):
        """
        Deducts funds from a customer's wallet if sufficient balance exists.
        """
        try:
            query = text("""
                UPDATE customers
                SET wallet_balance = wallet_balance - :amount
                WHERE username = :username AND wallet_balance >= :amount
            """)
            result = db.session.execute(query, {"amount": amount, "username": username})
            db.session.commit()
            return result.rowcount > 0
        except Exception as e:
            print(f"Error in deduct_wallet: {e}")
            db.session.rollback()
            return False

    def to_dict(self):
        """
        Converts the customer object to a dictionary.

        Returns:
            dict: A dictionary representation of the customer object.
        """
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "password": self.password,  # In production, passwords should be hashed and not exposed.
            "age": self.age,
            "address": self.address,
            "gender": self.gender,
            "marital_status": self.marital_status,
            "wallet_balance": self.wallet_balance,
        }