#!/bin/bash
# Build the Docker image
docker build -t fastapi-auth-app .

# Run the container
#docker run -p 8000:8000 fastapi-auth-app
docker run -p 8000:8000 -v $(pwd)/data:/app/data fastapi-auth-app
