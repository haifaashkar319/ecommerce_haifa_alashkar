# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the shared requirements file from the root
COPY requirements.txt ./requirements.txt

# Copy the source code for the service
COPY . .

COPY . /app
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
# Expose the service port
EXPOSE 5001
RUN apt-get update && apt-get install -y default-mysql-client

# Install netcat for the wait-for-db script



# Run the application
CMD ["python", "app.py"]

