from database.db_config import db
from inventory.models import Goods
from customers.models import Customer
from sales.models import Sale, PurchaseHistory

class SalesService:
    @staticmethod
    def display_goods():
        goods = Goods.query.filter(Goods.count_in_stock > 0).all()
        return [{"name": g.name, "price": g.price_per_item} for g in goods]

    @staticmethod
    def get_good_details(good_id):
        good = Goods.query.get(good_id)
        if not good:
            raise ValueError("Good not found")
        return good.to_dict()

    @staticmethod
    def process_sale(customer_username, good_id, quantity):
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
