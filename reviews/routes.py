from flask import Blueprint, request, jsonify
from reviews.services import ReviewService

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/', methods=['POST'])
def submit_review():
    """
    Submit a new review for a product.

    Expects a JSON payload with:
    - `customer_username` (str): Username of the customer submitting the review.
    - `product_id` (int): ID of the product being reviewed.
    - `rating` (int): Rating for the product (1-5).
    - `comment` (str, optional): Textual feedback.

    Returns:
        JSON response:
        - Success: The submitted review details (status code 201).
        - Error: An error message (status code 400).
    """
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
    """
    Update an existing review.

    Args:
        review_id (int): ID of the review to update.

    Expects a JSON payload with optional fields:
    - `rating` (int): New rating for the product (1-5).
    - `comment` (str): New textual feedback.

    Returns:
        JSON response:
        - Success: The updated review details (status code 200).
        - Error: An error message (status code 404).
    """
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
    """
    Delete a review.

    Args:
        review_id (int): ID of the review to delete.

    Returns:
        JSON response:
        - Success: A success message (status code 200).
        - Error: An error message (status code 404).
    """
    try:
        ReviewService.delete_review(review_id)
        return jsonify({"message": "Review deleted successfully"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """
    Retrieve all reviews for a specific product.

    Args:
        product_id (int): ID of the product.

    Returns:
        JSON response: A list of reviews for the product (status code 200).
    """
    reviews = ReviewService.get_product_reviews(product_id)
    return jsonify(reviews)

@reviews_bp.route('/customer/<string:customer_username>', methods=['GET'])
def get_customer_reviews(customer_username):
    """
    Retrieve all reviews submitted by a specific customer.

    Args:
        customer_username (str): Username of the customer.

    Returns:
        JSON response: A list of reviews by the customer (status code 200).
    """
    reviews = ReviewService.get_customer_reviews(customer_username)
    return jsonify(reviews)

@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    """
    Retrieve the details of a specific review.

    Args:
        review_id (int): ID of the review.

    Returns:
        JSON response:
        - Success: The review details (status code 200).
        - Error: An error message (status code 404).
    """
    try:
        review = ReviewService.get_review_details(review_id)
        return jsonify(review)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@reviews_bp.route('/<int:review_id>/moderate', methods=['PUT'])
def moderate_review(review_id):
    """
    Moderate a review (approve or reject).

    Args:
        review_id (int): ID of the review to moderate.

    Expects a JSON payload with:
    - `status` (str): The new status of the review ("approved" or "rejected").

    Returns:
        JSON response:
        - Success: The updated review details (status code 200).
        - Error: An error message (status code 400).
    """
    data = request.json
    try:
        review = ReviewService.moderate_review(
            review_id=review_id,
            status=data['status']
        )
        return jsonify(review)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
