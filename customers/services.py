from sqlalchemy.sql import text  
from database.db_config import db
from customers.models import Customer
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils import SECRET_KEY, create_token, extract_auth_token, decode_token, save_token


class CustomerService:
    @staticmethod
    def login_customer(username, password):
        """
        Verifies customer credentials and generates a token if valid.
        
        Args:
            username (str): The customer's username.
            password (str): The customer's password.
            
        Returns:
            dict: A dictionary with either the token or an error message.
        """
        try:
            customer = Customer.query.filter_by(username=username).first()
            if not customer or customer.password != password:
                return {"error": "Invalid username or password"}
            
            # Generate JWT token
            token = create_token(customer.id)
            return {"access_token": token}
        
        except SQLAlchemyError as e:
            return {"error": f"Database error: {str(e)}"}
    @staticmethod
    def save_to_db(customer):
        """
        Saves a customer object to the database.
        """
        query = text("""
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, role)
            VALUES (:full_name, :username, :password, :age, :address, :gender, :marital_status, :wallet_balance, :role)
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
                "wallet_balance": customer.wallet_balance or 0.0,
                "role": customer.role or "customer",  # Default role
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
            wallet_balance=result["wallet_balance"] or 0.0,
            role=result["role"]
        )
    
    @staticmethod
    def update_customer(username, updates):
        try:
            print(f"DEBUG: Attempting to update customer {username} with updates: {updates}")

            # Define all possible fields to update
            fields = [
                "full_name", "password", "age", "address",
                "gender", "marital_status", "wallet_balance", "role"
            ]

            # Include all fields in the update dictionary, defaulting to None for missing fields
            update_fields = {field: updates.get(field, None) for field in fields}
            update_fields["username"] = username

            query = text("""
                UPDATE customers
                SET
                    full_name = COALESCE(:full_name, full_name),
                    password = COALESCE(:password, password),
                    age = COALESCE(:age, age),
                    address = COALESCE(:address, address),
                    gender = COALESCE(:gender, gender),
                    marital_status = COALESCE(:marital_status, marital_status),
                    wallet_balance = COALESCE(:wallet_balance, wallet_balance),
                    role = COALESCE(:role, role)
                WHERE username = :username
            """)

            result = db.session.execute(query, update_fields)
            db.session.commit()

            print(f"DEBUG: Update query affected {result.rowcount} rows.")
            return result.rowcount > 0
        except Exception as e:
            print(f"DEBUG: Error in update_customer: {e}")
            db.session.rollback()
            return False

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
            wallet_balance=result["wallet_balance"],
            role=result["role"]
        ).to_dict() for result in results]
        
    @staticmethod
    def charge_wallet(username, amount):
        """
        Charges a specified amount to a customer's wallet.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to add to the wallet.

        Returns:
            bool: True if successful, False if the customer is not found or other errors occur.
        """
        try:
            # Log pre-update balance
            pre_query = text("SELECT wallet_balance FROM customers WHERE username = :username")
            pre_result = db.session.execute(pre_query, {"username": username}).mappings().fetchone()
            if not pre_result:
                print(f"DEBUG: Customer {username} not found.")
                return False

            print(f"DEBUG: Pre-update wallet balance for {username}: {pre_result['wallet_balance']}")

            # Update wallet balance
            query = text("""
                UPDATE customers
                SET wallet_balance = wallet_balance + :amount
                WHERE username = :username
            """)
            result = db.session.execute(query, {"amount": amount, "username": username})
            db.session.commit()

            # Log post-update balance
            post_query = text("SELECT wallet_balance FROM customers WHERE username = :username")
            post_result = db.session.execute(post_query, {"username": username}).mappings().fetchone()
            print(f"DEBUG: Post-update wallet balance for {username}: {post_result['wallet_balance']}")

            return result.rowcount > 0
        except Exception as e:
            print(f"Error in charge_wallet: {e}")
            db.session.rollback()
            return False


    @staticmethod
    def deduct_wallet(username, amount):
        """
        Deducts funds from a customer's wallet if sufficient balance exists.

        Args:
            username (str): The username of the customer.
            amount (float): The amount to deduct.

        Returns:
            bool: True if successful, False if the customer doesn't exist or has insufficient funds.
        """
        try:
            # Log pre-update balance
            pre_query = text("SELECT wallet_balance FROM customers WHERE username = :username")
            pre_result = db.session.execute(pre_query, {"username": username}).mappings().fetchone()
            if not pre_result:
                print(f"DEBUG: Customer {username} not found.")
                return False

            print(f"DEBUG: Pre-update wallet balance for {username}: {pre_result['wallet_balance']}")

            # Ensure sufficient balance before deducting
            if pre_result['wallet_balance'] < amount:
                print(f"DEBUG: Insufficient funds for {username}. Cannot deduct {amount} from balance {pre_result['wallet_balance']}.")
                return False

            # Update wallet balance
            query = text("""
                UPDATE customers
                SET wallet_balance = wallet_balance - :amount
                WHERE username = :username
            """)
            result = db.session.execute(query, {"amount": amount, "username": username})
            db.session.commit()

            # Log post-update balance
            post_query = text("SELECT wallet_balance FROM customers WHERE username = :username")
            post_result = db.session.execute(post_query, {"username": username}).mappings().fetchone()
            print(f"DEBUG: Post-update wallet balance for {username}: {post_result['wallet_balance']}")

            return result.rowcount > 0
        except Exception as e:
            print(f"Error in charge_wallet: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def delete_customer(username):
        """
        Deletes a customer from the database.

        Args:
            username (str): The username of the customer to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            query = text("DELETE FROM customers WHERE username = :username")
            result = db.session.execute(query, {"username": username})
            db.session.commit()
            return result.rowcount > 0
        except Exception as e:
            print(f"Error in delete_customer: {e}")
            db.session.rollback()
            return False
    def validate_customer_payload(payload):
        required_fields = ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']
        missing_fields = [field for field in required_fields if field not in payload]

        if missing_fields:
            raise ValueError(f"Missing fields: {', '.join(missing_fields)}")


