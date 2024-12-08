# Use Python base image
FROM python:3.9-slim

ENV PYTHONPATH=/app
# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5004

# Run the application
CMD ["python", "app.py"]
