FROM python:3.11

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Upgrade pip using python -m pip (more reliable)
RUN python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create uploads directory
RUN mkdir -p ./uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
