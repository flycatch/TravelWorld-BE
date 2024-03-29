# Use an official Python runtime as a parent image
FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app/
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app/
COPY . /app/


