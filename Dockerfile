# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and folders
COPY process_pdfs.py .
COPY input ./input

# Ensure output directory exists
RUN mkdir -p /app/output

# Run the script
CMD ["python", "process_pdfs.py"]
