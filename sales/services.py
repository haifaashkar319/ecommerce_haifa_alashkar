from database.db_config import db
from inventory.models import Goods
from customers.models import Customer
from sales.models import Sale, PurchaseHistory

class SalesService:
    """
    Service class for handling sales-related operations.

    This class provides methods for:
    - Displaying available goods.
    - Retrieving details of a specific good.
    - Processing a sale by validating customer and stock availability.
    """

    @staticmethod
    def display_goods():
        """
        Fetches all available goods with stock greater than zero.

        Returns:
            list: A list of dictionaries containing:
                - `name` (str): The name of the good.
                - `price` (float): The price per item of the good.
        """
        goods = Goods.query.filter(Goods.count_in_stock > 0).all()
        return [{"name": g.name, "price": g.price_per_item} for g in goods]

    @staticmethod
    def get_good_details(good_id):
        """
        Retrieves details for a specific good.

        Args:
            good_id (int): The ID of the good to retrieve.

        Returns:
            dict: A dictionary containing the details of the good.

        Raises:
            ValueError: If the good with the specified ID does not exist.
        """
        good = Goods.query.get(good_id)
        if not good:
            raise ValueError("Good not found")
        return good.to_dict()

    @staticmethod
    def process_sale(customer_username, good_id, quantity):
        """
        Processes a sale transaction.

        This method validates the customer, checks stock availability, and
        deducts the customer's wallet balance and the stock quantity if all
        conditions are met. It also records the sale and updates the purchase
        history.

        Args:
            customer_username (str): The username of the customer making the purchase.
            good_id (int): The ID of the good being purchased.
            quantity (int): The quantity of the good to purchase.

        Returns:
            dict: A dictionary containing the details of the processed sale.

        Raises:
            ValueError: If:
                - The customer does not exist.
                - The good does not exist or has insufficient stock.
                - The customer's wallet balance is insufficient.
        """
        # Fetch the customer and good
        customer = Customer.query.filter_by(username=customer_username).first()
        good = Goods.query.get(good_id)

        if not customer:
            raise ValueError("Customer not found")
        if not good or good.count_in_stock < quantity:
            raise ValueError("Good not available or insufficient stock")
        
        total_price = good.price_per_item * quantity
        if customer.wallet_balance < total_price:
            raise ValueError("Insufficient wallet balance")

        # Deduct stock and wallet balance
        good.count_in_stock -= quantity
        customer.wallet_balance -= total_price

        # Record the sale
        sale = Sale(
            good_id=good_id,
            customer_username=customer_username,
            quantity=quantity,
            total_price=total_price
        )
        db.session.add(sale)

        # Record the purchase in history
        history = PurchaseHistory(
            customer_username=customer_username,
            good_name=good.name,
            total_price=total_price
        )
        db.session.add(history)

        db.session.commit()
        return sale.to_dict()
