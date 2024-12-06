from flask import Blueprint, request, jsonify
from utils import SECRET_KEY, extract_auth_token, decode_token
from customers.models import Customer
from reviews.services import ReviewService
from sqlalchemy.exc import SQLAlchemyError
import jwt
reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# Your JWT_SECRET_KEY (make sure it matches the one used during token generation)
JWT_SECRET_KEY = "your-secret-key"

@reviews_bp.route('/', methods=['POST'])
def submit_review():
    """
    Submit a new review for a product.

    Expects a JSON payload with:
    - `product_id` (int): ID of the product being reviewed.
    - `rating` (int): Rating for the product (1-5).
    - `comment` (str, optional): Textual feedback.

    Requires an Authorization token in the header to identify the user.

    Returns:
        JSON response:
        - Success: The submitted review details (status code 201).
        - Error: An error message (status code 400 or 403).
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

        # Verify user existence
        existing_user = Customer.query.get(user_id)
        if not existing_user:
            return jsonify({"error": "Unauthorized"}), 403

        # Parse review details from request
        data = request.json
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        # Input validation
        if not product_id or not rating:
            return jsonify({"error": "Product ID and rating are required"}), 400

        try:
            # Submit the review using the service
            review = ReviewService.submit_review(
                customer_username=existing_user.username,
                product_id=product_id,
                rating=rating,
                comment=comment
            )
            return jsonify(review), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # If no header or invalid header
    return jsonify({"error": "Authorization header missing or malformed"}), 403


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Update an existing review.

    Args:
        review_id (int): ID of the review to update.

    Expects a JSON payload with optional fields:
    - `rating` (int): New rating for the product (1-5).
    - `comment` (str): New textual feedback.

    Requires an Authorization token in the header to identify the user.

    Returns:
        JSON response:
        - Success: The updated review details (status code 200).
        - Error: An error message (status code 404 or 403).
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

        # Verify user existence
        existing_user = Customer.query.get(user_id)
        if not existing_user:
            return jsonify({"error": "Unauthorized"}), 403

        # Parse review details from request
        data = request.json
        try:
            # Update the review using the service
            review = ReviewService.update_review(
                review_id=review_id,
                rating=data.get('rating'),
                comment=data.get('comment')
            )
            return jsonify(review)
        except ValueError as e:
            # Handle specific validation errors
            if "Rating must be between 1 and 5" in str(e):
                return jsonify({"error": str(e)}), 400
            elif "Review not found" in str(e):
                return jsonify({"error": str(e)}), 404
            # Handle unexpected errors
            return jsonify({"error": "An unknown error occurred"}), 400

    # If no header or invalid header
    return jsonify({"error": "Authorization header missing or malformed"}), 403

@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete a review.

    Args:
        review_id (int): ID of the review to delete.

    Requires an Authorization token in the header to identify the user.

    Returns:
        JSON response:
        - Success: A success message (status code 200).
        - Error: An error message (status code 404 or 403).
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

        # Verify user existence
        existing_user = Customer.query.get(user_id)
        if not existing_user:
            return jsonify({"error": "Unauthorized"}), 403

        try:
            ReviewService.delete_review(review_id)
            return jsonify({"message": "Review deleted successfully"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    # If no header or invalid header
    return jsonify({"error": "Authorization header missing or malformed"}), 403

@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """
    Retrieve all reviews for a specific product.

    Args:
        product_id (int): ID of the product.

    Returns:
        JSON response: A list of reviews for the product (status code 200).
    """
    try:
        reviews = ReviewService.get_product_reviews(product_id)
        return jsonify(reviews)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/customer/<string:customer_username>', methods=['GET'])
def get_customer_reviews(customer_username):
    """
    Retrieve all reviews submitted by a specific customer.

    Args:
        customer_username (str): Username of the customer.

    Returns:
        JSON response: A list of reviews by the customer (status code 200).
    """
    try:
        reviews = ReviewService.get_customer_reviews(customer_username)
        return jsonify(reviews)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


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

    Requires an Authorization token in the header to identify the user.

    Returns:
        JSON response:
        - Success: The updated review details (status code 200).
        - Error: An error message (status code 400 or 403).
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

        # Verify user existence
        existing_user = Customer.query.get(user_id)
        if not existing_user:
            return jsonify({"error": "Unauthorized"}), 403
        if existing_user.role != "admin":
            return jsonify({"error": "Must be admin"})
        # Parse moderation details from request
        data = request.json
        try:
            review = ReviewService.moderate_review(
                review_id=review_id,
                status=data['status']
            )
            return jsonify(review), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # If no header or invalid header
    return jsonify({"error": "Authorization header missing or malformed"}), 403
