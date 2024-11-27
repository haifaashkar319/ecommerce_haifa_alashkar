from flask import Blueprint, request, jsonify
from reviews.services import ReviewService

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/', methods=['POST'])
def submit_review():
    data = request.json
    try:
        review = ReviewService.submit_review(
            customer_username=data['customer_username'],
            product_id=data['product_id'],
            rating=data['rating'],
            comment=data.get('comment')
        )
        return jsonify(review), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@reviews_bp.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.json
    try:
        review = ReviewService.update_review(
            review_id=review_id,
            rating=data.get('rating'),
            comment=data.get('comment')
        )
        return jsonify(review)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        ReviewService.delete_review(review_id)
        return jsonify({"message": "Review deleted successfully"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = ReviewService.get_product_reviews(product_id)
    return jsonify(reviews)

@reviews_bp.route('/customer/<string:customer_username>', methods=['GET'])
def get_customer_reviews(customer_username):
    reviews = ReviewService.get_customer_reviews(customer_username)
    return jsonify(reviews)

@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    try:
        review = ReviewService.get_review_details(review_id)
        return jsonify(review)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@reviews_bp.route('/<int:review_id>/moderate', methods=['PUT'])
def moderate_review(review_id):
    data = request.json
    try:
        review = ReviewService.moderate_review(
            review_id=review_id,
            status=data['status']
        )
        return jsonify(review)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
