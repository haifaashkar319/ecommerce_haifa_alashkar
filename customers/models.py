class Customer:
    """
    Represents a customer in the system.

    Attributes:
        full_name (str): The full name of the customer.
        username (str): The unique username of the customer.
        password (str): The password for the customer (should ideally be hashed).
        age (int): The age of the customer.
        address (str, optional): The address of the customer. Defaults to None.
        gender (str, optional): The gender of the customer. Defaults to None.
        marital_status (str, optional): The marital status of the customer. Defaults to None.
        wallet_balance (float, optional): The wallet balance of the customer. Defaults to 0.0.
    """

    def __init__(self, full_name, username, password, age, address=None, gender=None, marital_status=None, wallet_balance=0.0):
        """
        Initializes a Customer object.

        Args:
            full_name (str): The full name of the customer.
            username (str): The unique username of the customer.
            password (str): The password for the customer.
            age (int): The age of the customer.
            address (str, optional): The address of the customer. Defaults to None.
            gender (str, optional): The gender of the customer. Defaults to None.
            marital_status (str, optional): The marital status of the customer. Defaults to None.
            wallet_balance (float, optional): The wallet balance of the customer. Defaults to 0.0.
        """
        self.full_name = full_name
        self.username = username
        self.password = password
        self.age = age
        self.address = address
        self.gender = gender
        self.marital_status = marital_status
        self.wallet_balance = wallet_balance

    def charge_wallet(self, amount):
        """
        Adds funds to the customer's wallet.

        Args:
            amount (float): The amount to add to the wallet.
        """
        self.wallet_balance += amount

    def deduct_wallet(self, amount):
        """
        Deducts funds from the customer's wallet if sufficient balance exists.

        Args:
            amount (float): The amount to deduct from the wallet.

        Raises:
            ValueError: If the amount exceeds the available wallet balance.
        """
        if amount > self.wallet_balance:
            raise ValueError("Insufficient funds in wallet.")
        self.wallet_balance -= amount

    def to_dict(self):
        """
        Converts the customer object to a dictionary.

        Returns:
            dict: A dictionary representation of the customer object, suitable for API responses.
        """
        return {
            "full_name": self.full_name,
            "username": self.username,
            "password": self.password,  # Ideally, this would be hashed.
            "age": self.age,
            "address": self.address,
            "gender": self.gender,
            "marital_status": self.marital_status,
            "wallet_balance": self.wallet_balance,
        }
