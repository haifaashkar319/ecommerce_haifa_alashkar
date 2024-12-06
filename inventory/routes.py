from flask import Blueprint, request, jsonify
from inventory.services import InventoryService, UnauthorizedAccess
from sqlalchemy.exc import SQLAlchemyError

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
    try:
        InventoryService.require_admin_role(request)
        data = request.json
        goods = InventoryService.add_goods(
            name=data['name'],
            category=data['category'],
            price_per_item=data['price_per_item'],
            description=data.get('description'),
            count_in_stock=data['count_in_stock']
        )
        return jsonify(goods), 201
    except UnauthorizedAccess as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

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
    try:
        InventoryService.require_admin_role(request)
        data = request.json
        goods = InventoryService.update_goods(goods_id, data)
        return jsonify(goods), 200
    except UnauthorizedAccess as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


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
        return jsonify(goods), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@inventory_bp.route('/', methods=['GET'])
def get_all_goods():
    """
    API to retrieve all goods from the inventory.

    Returns:
        JSON response with a list of all goods.
    """
    try:
        goods = InventoryService.get_all_goods()
        return jsonify(goods), 200
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@inventory_bp.route('/<int:goods_id>/deduct', methods=['POST'])
def deduct_goods_stock(goods_id):
    """
    API to deduct a specific quantity of goods from the inventory.

    Requires an Authorization token in the header to identify the user and validate admin privileges.

    Args:
        goods_id (int): ID of the goods.

    Expects:
    - quantity (int): Number of items to deduct.

    Returns:
        JSON response with the updated goods details.
    """
    try:
        InventoryService.require_admin_role(request)
        data = request.json
        if not data or "quantity" not in data:
            return jsonify({"error": "Quantity is required"}), 400

        quantity = data['quantity']
        if quantity <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400

        goods = InventoryService.deduct_goods(goods_id, quantity)
        return jsonify({"message": f"Successfully deducted {quantity} from stock.", "updated_stock": goods}), 200
    except UnauthorizedAccess as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
