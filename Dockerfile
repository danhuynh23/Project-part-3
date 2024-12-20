# Use a more comprehensive Python base image
FROM python:3.11-bullseye

# Set the working directory
WORKDIR /app

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "system:app"]
