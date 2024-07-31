# Use the official Nginx image from the Docker Hub
FROM nginx:stable-alpine

# Copy custom configuration file from the current directory
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static and media files from the frontend build
COPY frontend/imaglee-app/dist /usr/share/nginx/html

# Expose ports for HTTP and HTTPS
EXPOSE 80
EXPOSE 443