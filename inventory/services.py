from flask import jsonify
import jwt
from sqlalchemy.exc import SQLAlchemyError
from customers.models import Customer
from utils import decode_token
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

        if quantity > goods.count_in_stock:
            raise ValueError("Insufficient stock available")

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
    
    @staticmethod
    def require_admin_role(request):
        print("Entering require_admin_role")
        header = request.headers.get("Authorization")
        print(f"Authorization Header: {header}")  # Debug log

        if not header:
            raise UnauthorizedAccess("Authorization header missing or malformed")

        try:
            user_id = decode_token(header)
            print(f"Decoded User ID: {user_id}")
        except jwt.ExpiredSignatureError:
            raise UnauthorizedAccess("Token has expired")
        except jwt.InvalidTokenError as e:
            raise UnauthorizedAccess(f"Unauthorized: {e}")

        user = Customer.query.get(user_id)
        print(f"Fetched User: {user}")  # Debug log
        if user:
            print(f"User Role: {user.role}")
        else:
            print("No user found with this ID.")

        if not user or user.role != "admin":
            print("User is not authorized")
            raise UnauthorizedAccess("Access forbidden: Admins only")

        print("User is authorized")
        return user


class UnauthorizedAccess(Exception):
    """Custom exception for unauthorized access."""
    pass


