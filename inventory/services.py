from sqlalchemy.exc import SQLAlchemyError
from inventory.models import Goods
from database.db_config import db

class InventoryService:
    """
    Service layer for managing inventory operations.
    """

    @staticmethod
    def add_goods(name, category, price_per_item, description, count_in_stock):
        """
        Add new goods to the inventory.
        """
        goods = Goods(
            name=name,
            category=category,
            price_per_item=price_per_item,
            description=description,
            count_in_stock=count_in_stock
        )
        db.session.add(goods)
        try:
            db.session.commit()
            return goods.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to add goods: {e}")

    @staticmethod
    def update_goods(goods_id, updates):
        """
        Update fields of a specific goods item.
        """
        goods = Goods.query.get(goods_id)
        if not goods:
            raise ValueError("Goods not found.")

        for key, value in updates.items():
            if hasattr(goods, key):
                setattr(goods, key, value)

        try:
            db.session.commit()
            return goods.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to update goods: {e}")

    @staticmethod
    def deduct_goods(goods_id, quantity):
        """
        Deduct items from inventory.
        """
        goods = Goods.query.get(goods_id)
        if not goods:
            raise ValueError("Goods not found.")

        try:
            goods.deduct_stock(quantity)
            db.session.commit()
            return goods.to_dict()
        except ValueError as e:
            raise ValueError(f"Error deducting goods: {e}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to deduct goods: {e}")

    @staticmethod
    def get_goods_by_id(goods_id):
        """
        Retrieve goods by ID.
        """
        goods = Goods.query.get(goods_id)
        if not goods:
            raise ValueError("Goods not found.")
        return goods.to_dict()

    @staticmethod
    def get_all_goods():
        """
        Retrieve all goods from inventory.
        """
        goods_list = Goods.query.all()
        return [goods.to_dict() for goods in goods_list]
