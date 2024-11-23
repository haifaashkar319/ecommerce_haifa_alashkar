from sqlalchemy.sql import text  
from database.db_config import db
from customers.models import Customer

class CustomerService:
    @staticmethod
    def save_to_db(customer):
        """Saves a customer object to the database."""
        query = text("""
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance)
            VALUES (:full_name, :username, :password, :age, :address, :gender, :marital_status, :wallet_balance)
        """)
        db.session.execute(
            query,
            {
                "full_name": customer.full_name,
                "username": customer.username,
                "password": customer.password,
                "age": customer.age,
                "address": customer.address,
                "gender": customer.gender,
                "marital_status": customer.marital_status,
                "wallet_balance": customer.wallet_balance,
            },
        )
        db.session.commit()

    @staticmethod
    def get_customer_by_username(username):
        """Fetches a customer record from the database by username."""
        query = text("SELECT * FROM customers WHERE username = :username")
        result = db.session.execute(query, {"username": username}).fetchone()

        if not result:
            return None

        return Customer(
            full_name=result["full_name"],
            username=result["username"],
            password=result["password"],
            age=result["age"],
            address=result["address"],
            gender=result["gender"],
            marital_status=result["marital_status"],
            wallet_balance=result["wallet_balance"],
        )
