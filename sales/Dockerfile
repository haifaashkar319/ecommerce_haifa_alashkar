# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the shared requirements file from the root
COPY requirements.txt ./requirements.txt


COPY . /app
# Copy the source code for the service
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the service port
EXPOSE 5003

# Run the application
CMD ["python", "app.py"]
