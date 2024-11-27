from database.db_config import db
from reviews.models import Review
from customers.models import Customer
from inventory.models import Goods

class ReviewService:
    """
    Handles the business logic for reviews.
    """

    @staticmethod
    def submit_review(customer_username, product_id, rating, comment):
        """
        Submits a new review for a product.

        Args:
            customer_username (str): The username of the customer.
            product_id (int): The ID of the product.
            rating (int): The rating (1-5).
            comment (str): The textual feedback.

        Returns:
            dict: The submitted review details.

        Raises:
            ValueError: If the customer or product does not exist.
        """
        customer = Customer.query.filter_by(username=customer_username).first()
        product = Goods.query.get(product_id)

        if not customer:
            raise ValueError("Customer not found")
        if not product:
            raise ValueError("Product not found")
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        review = Review(
            customer_username=customer_username,
            product_id=product_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review.to_dict()

    @staticmethod
    def update_review(review_id, rating=None, comment=None):
        """
        Updates an existing review.

        Args:
            review_id (int): The ID of the review to update.
            rating (int, optional): The new rating.
            comment (str, optional): The new comment.

        Returns:
            dict: The updated review details.

        Raises:
            ValueError: If the review does not exist.
        """
        review = Review.query.get(review_id)
        if not review:
            raise ValueError("Review not found")
        if rating:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            review.rating = rating
        if comment:
            review.comment = comment
        db.session.commit()
        return review.to_dict()

    @staticmethod
    def delete_review(review_id):
        """
        Deletes a review.

        Args:
            review_id (int): The ID of the review to delete.

        Raises:
            ValueError: If the review does not exist.
        """
        review = Review.query.get(review_id)
        if not review:
            raise ValueError("Review not found")
        db.session.delete(review)
        db.session.commit()

    @staticmethod
    def get_product_reviews(product_id):
        """
        Retrieves all reviews for a product.

        Args:
            product_id (int): The ID of the product.

        Returns:
            list: A list of reviews.
        """
        return [review.to_dict() for review in Review.query.filter_by(product_id=product_id).all()]

    @staticmethod
    def get_customer_reviews(customer_username):
        """
        Retrieves all reviews submitted by a customer.

        Args:
            customer_username (str): The username of the customer.

        Returns:
            list: A list of reviews.
        """
        return [review.to_dict() for review in Review.query.filter_by(customer_username=customer_username).all()]

    @staticmethod
    def get_review_details(review_id):
        """
        Retrieves the details of a specific review.

        Args:
            review_id (int): The ID of the review.

        Returns:
            dict: The review details.

        Raises:
            ValueError: If the review does not exist.
        """
        review = Review.query.get(review_id)
        if not review:
            raise ValueError("Review not found")
        return review.to_dict()
    @staticmethod
    def moderate_review(review_id, status):
        """
        Moderates a review by updating its status.

        Args:
            review_id (int): The ID of the review to moderate.
            status (str): The new status ('approved' or 'flagged').

        Returns:
            dict: The updated review details.

        Raises:
            ValueError: If the review does not exist or status is invalid.
        """
        review = Review.query.get(review_id)
        if not review:
            raise ValueError("Review not found")
        if status not in ['approved', 'flagged']:
            raise ValueError("Invalid status. Must be 'approved' or 'flagged'")
        review.status = status
        db.session.commit()
        return review.to_dict()
