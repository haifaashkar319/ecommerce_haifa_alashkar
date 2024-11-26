from flask import Blueprint, request, jsonify
from sales.services import SalesService

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/goods', methods=['GET'])
def display_goods():
    try:
        goods = SalesService.display_goods()
        return jsonify(goods)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sales_bp.route('/goods/<int:good_id>', methods=['GET'])
def get_good_details(good_id):
    try:
        good_details = SalesService.get_good_details(good_id)
        return jsonify(good_details)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@sales_bp.route('/purchase', methods=['POST'])
def process_sale():
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
