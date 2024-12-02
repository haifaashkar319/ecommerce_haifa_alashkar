from flask import Blueprint, request, jsonify
from sales.services import SalesService
from utils import SECRET_KEY, extract_auth_token, decode_token
import jwt
sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/goods', methods=['GET'])
def display_goods():
    """
    API endpoint to retrieve a list of available goods.

    Returns:
        Response (JSON): A list of goods with their names and prices.
    """
    try:
        goods = SalesService.display_goods()
        return jsonify(goods)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sales_bp.route('/goods/<int:good_id>', methods=['GET'])
def get_good_details(good_id):
    """
    API endpoint to retrieve detailed information about a specific good.

    Args:
        good_id (int): The ID of the good.

    Returns:
        Response (JSON): The details of the good or an error message if not found.
    """
    try:
        good_details = SalesService.get_good_details(good_id)
        return jsonify(good_details)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@sales_bp.route('/purchase', methods=['POST'])
def process_sale():
    """
    API endpoint to process a sale.

    Requires an Authorization token in the header to identify the user.

    Expects:
        JSON payload with:
        - good_id (int): The ID of the good being purchased.
        - quantity (int): The quantity of the good being purchased.

    Returns:
        Response (JSON): The sale details if successful or an error message otherwise.
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

        # Parse sale details from request
        data = request.json
        good_id = data.get('good_id')
        quantity = data.get('quantity')

        # Input validation
        if not good_id or not quantity:
            return jsonify({"error": "Good ID and quantity are required"}), 400

        try:
            # Process the sale using the service
            sale = SalesService.process_sale(
                customer_id=user_id,
                good_id=good_id,
                quantity=quantity
            )
            return jsonify(sale), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # If no header or invalid header
    return jsonify({"error": "Authorization header missing or malformed"}), 403
