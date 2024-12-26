# Use Python 3.9 as base image
FROM python:3.11.4

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ./src/ /app/

# Run OS-level updates and install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3-venv python3-dev python3-pip

# Create the Python virtual environment
RUN python3 -m venv /opt/ven

# Upgrade pip inside the virtual environment
RUN /opt/venv/bin/python -m pip install --upgrade pip

# Install project dependencies from requirements.txt
RUN /opt/venv/bin/python -m pip install -r requirements.txt

# copy our local conf/entrypoint.sh to /app in the container
COPY ./conf/entrypoint.sh /app/entrypoint.sh

# Make our entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Execute our entrypoint script
CMD ["./entrypoint.sh"]
