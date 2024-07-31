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

# Make port 9000 available to the world outside this container
EXPOSE 9000

# Run the application
CMD ["npm", "start"]