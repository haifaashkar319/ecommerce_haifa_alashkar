class Customer:
    def __init__(self, full_name, username, password, age, address=None, gender=None, marital_status=None, wallet_balance=0.0):
        self.full_name = full_name
        self.username = username
        self.password = password
        self.age = age
        self.address = address
        self.gender = gender
        self.marital_status = marital_status
        self.wallet_balance = wallet_balance

    def charge_wallet(self, amount):
        """Adds funds to the wallet."""
        self.wallet_balance += amount

    def deduct_wallet(self, amount):
        """Deducts funds from the wallet if sufficient balance exists."""
        if amount > self.wallet_balance:
            raise ValueError("Insufficient funds in wallet.")
        self.wallet_balance -= amount

    def to_dict(self):
        """Converts the customer object to a dictionary (for API responses)."""
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
