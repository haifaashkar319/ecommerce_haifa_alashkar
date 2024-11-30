from flask import Blueprint, request, jsonify
from inventory.services import InventoryService
from utils import SECRET_KEY, extract_auth_token, decode_token
import jwt

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/', methods=['POST'])
def add_goods():
    """
    API to add new goods to the inventory.

    Requires an Authorization token in the header to identify the user.

    Expects:
    - name (str): Name of the goods.
    - category (str): Category of the goods.
    - price_per_item (float): Price per item.
    - description (str, optional): Description of the goods.
    - count_in_stock (int): Number of items in stock.

    Returns:
        JSON response with the created goods details.
    """
    # Extract and validate token
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        try:
            goods = InventoryService.add_goods(
                name=data['name'],
                category=data['category'],
                price_per_item=data['price_per_item'],
                description=data.get('description'),
                count_in_stock=data['count_in_stock']
            )
            return jsonify(goods), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@inventory_bp.route('/<int:goods_id>', methods=['PUT'])
def update_goods(goods_id):
    """
    API to update fields of a specific goods item.

    Requires an Authorization token in the header to identify the user.

    Args:
        goods_id (int): ID of the goods to update.

    Expects a JSON payload with the fields to update.

    Returns:
        JSON response with the updated goods details.
    """
    # Extract and validate token
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        try:
            goods = InventoryService.update_goods(goods_id, data)
            return jsonify(goods)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@inventory_bp.route('/<int:goods_id>', methods=['DELETE'])
def deduct_goods(goods_id):
    """
    API to deduct a specific quantity of goods from the inventory.

    Requires an Authorization token in the header to identify the user.

    Args:
        goods_id (int): ID of the goods.

    Expects:
    - quantity (int): Number of items to deduct.

    Returns:
        JSON response with the updated goods details.
    """
    # Extract and validate token
    header = extract_auth_token(request)
    if header:
        try:
            user_id = decode_token(header)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.json
        if not data or "quantity" not in data:
            return jsonify({"error": "Quantity is required"}), 400

        try:
            goods = InventoryService.deduct_goods(goods_id, data['quantity'])
            return jsonify(goods)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Authorization header missing or malformed"}), 403

@inventory_bp.route('/<int:goods_id>', methods=['GET'])
def get_goods(goods_id):
    """
    API to retrieve goods by ID.

    Args:
        goods_id (int): ID of the goods.

    Returns:
        JSON response with the goods details.
    """
    try:
        goods = InventoryService.get_goods_by_id(goods_id)
        return jsonify(goods)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@inventory_bp.route('/', methods=['GET'])
def get_all_goods():
    """
    API to retrieve all goods from the inventory.

    Returns:
        JSON response with a list of all goods.
    """
    goods = InventoryService.get_all_goods()
    return jsonify(goods)
