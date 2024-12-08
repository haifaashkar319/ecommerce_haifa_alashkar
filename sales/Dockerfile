# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

ENV PYTHONPATH=/app
# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5003

# Run the application
CMD ["python", "app.py"]
