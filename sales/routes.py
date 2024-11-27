from flask import Blueprint, request, jsonify
from sales.services import SalesService

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

    Expects:
        JSON payload with:
        - customer_username (str): The username of the customer.
        - good_id (int): The ID of the good being purchased.
        - quantity (int): The quantity of the good being purchased.

    Returns:
        Response (JSON): The sale details if successful or an error message otherwise.
    """
    data = request.json
    try:
        sale = SalesService.process_sale(
            customer_username=data['customer_username'],
            good_id=data['good_id'],
            quantity=data['quantity']
        )
        return jsonify(sale), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
