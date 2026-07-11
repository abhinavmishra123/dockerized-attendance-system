# Use the official Python image as a base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set an environment variable
ENV APP_ENV=Docker

# Expose port 5000 to the outside world (since Flask runs on 5000)
EXPOSE 5000

# Command to run the application when the container starts
CMD ["python", "app.py"]
