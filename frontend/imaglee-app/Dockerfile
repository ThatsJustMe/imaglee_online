# Use the official Node.js image from the Docker Hub
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files into the container
COPY package*.json ./

# Install any dependencies
RUN npm install

# Copy the current directory contents into the container
COPY . .

# Build the app for production with minification
RUN npm run build

# Install serve to serve the build files
RUN npm install -g serve

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["serve", "-s", "dist"]
