FROM python:3.10-slim

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
