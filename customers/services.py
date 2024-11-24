from sqlalchemy.sql import text  
from database.db_config import db
from customers.models import Customer

class CustomerService:
    @staticmethod
    def save_to_db(customer):
        """
        Saves a customer object to the database.

        Args:
            customer (Customer): The customer object to save.

        Returns:
            None
        """
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
        """
        Fetches a customer record from the database by username.

        Args:
            username (str): The username of the customer.

        Returns:
            Customer or None: The customer object if found, otherwise None.
        """
        query = text("SELECT * FROM customers WHERE username = :username")
        result = db.session.execute(query, {"username": username}).mappings().fetchone()

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
    
    @staticmethod
    def update_customer(username, updates):
        """
        Updates a customer's information.

        Args:
            username (str): The username of the customer.
            updates (dict): A dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        query = text("""
            UPDATE customers
            SET full_name = COALESCE(:full_name, full_name),
                password = COALESCE(:password, password),
                age = COALESCE(:age, age),
                address = COALESCE(:address, address),
                gender = COALESCE(:gender, gender),
                marital_status = COALESCE(:marital_status, marital_status),
                wallet_balance = COALESCE(:wallet_balance, wallet_balance)
            WHERE username = :username
        """)
        result = db.session.execute(
            query, {**updates, "username": username}
        )
        db.session.commit()
        return result.rowcount > 0
    
    @staticmethod
    def delete_customer(username):
        """
        Deletes a customer from the database.

        Args:
            username (str): The username of the customer.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        query = text("DELETE FROM customers WHERE username = :username")
        result = db.session.execute(query, {"username": username})
        db.session.commit()
        return result.rowcount > 0

    @staticmethod
    def get_all_customers():
        """
        Fetches all customers from the database.

        Returns:
            list: A list of customer dictionaries.
        """
        query = text("SELECT * FROM customers")
        results = db.session.execute(query).mappings().fetchall()

        return [Customer(
            full_name=result["full_name"],
            username=result["username"],
            password=result["password"],
            age=result["age"],
            address=result["address"],
            gender=result["gender"],
            marital_status=result["marital_status"],
            wallet_balance=result["wallet_balance"]
        ).to_dict() for result in results]
        
    @staticmethod
    def charge_wallet(username, amount):
        """
        Charges a specified amount to a customer's wallet.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to charge.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        query = text("""
            UPDATE customers
            SET wallet_balance = wallet_balance + :amount
            WHERE username = :username
        """)
        result = db.session.execute(query, {"amount": amount, "username": username})
        db.session.commit()
        return result.rowcount > 0

    @staticmethod
    def deduct_wallet(username, amount):
        """
        Deducts funds from a customer's wallet if sufficient balance exists.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to deduct.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        query = text("""
            UPDATE customers
            SET wallet_balance = wallet_balance - :amount
            WHERE username = :username AND wallet_balance >= :amount
        """)
        result = db.session.execute(query, {"amount": amount, "username": username})
        db.session.commit()
        return result.rowcount > 0
