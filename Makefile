# Variables
CONTAINER_NAME = ecommerce-mysql
MYSQL_ROOT_PASSWORD = Haifa319*
PORT = 3307:3306
VOLUME = mysql_data:/var/lib/mysql
IMAGE = mysql:latest

# Commands
db-start:
	docker start $(CONTAINER_NAME) || docker run --name $(CONTAINER_NAME) -e MYSQL_ROOT_PASSWORD=$(MYSQL_ROOT_PASSWORD) -d -p $(PORT) -v $(VOLUME) $(IMAGE)

db-stop:
	docker stop $(CONTAINER_NAME) || echo "Container $(CONTAINER_NAME) is not running."

db-remove:
	docker rm -f $(CONTAINER_NAME) || echo "Container $(CONTAINER_NAME) does not exist."

db-clean:
	docker volume rm $(VOLUME) || echo "Volume $(VOLUME) does not exist."

db-reset:
	make db-remove
	make db-clean
	make db-start

# Flask App
FLASK_APP = main.py

# Start Flask App
flask-start:
	@echo "Starting Flask app..."
	python $(FLASK_APP)

# Stop Flask App
flask-stop:
	@echo "Stopping Flask app..."
	@pkill -f $(FLASK_APP) || echo "Flask app is not running."

# Testing Commands
test-reviews:
	@echo "Running tests for reviews service..."
	pytest -s tests/test_reviews_service.py -W ignore::DeprecationWarning

test-customers:
	@echo "Running tests for customers service..."
	pytest -s tests/test_customer_service.py -W ignore::DeprecationWarning

test-inventory:
	@echo "Running tests for inventory service..."
	pytest -s tests/test_inventory_service.py -W ignore::DeprecationWarning

test-sales:
	@echo "Running tests for sales service..."
	pytest -s tests/test_sales_service.py -W ignore::DeprecationWarning

test-all:
	@echo "Running all tests..."
	pytest -s tests/ -W ignore::DeprecationWarning
