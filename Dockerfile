# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies from requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy all other files (your app.py, templates folder, etc.) into the container at /app
COPY . .

# Cloud Run expects the app to listen on the port specified by the PORT environment variable.
# We default to 8080, but Cloud Run will provide this.
ENV PORT 8080
EXPOSE 8080

# Command to run the Flask app using Gunicorn (a production-ready web server)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
