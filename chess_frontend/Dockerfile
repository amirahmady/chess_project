# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React application
RUN npm run build

# Install serve to serve the build files
RUN npm install -g serve

# Copy serve.json to the build directory
COPY serve.json ./build/


# Set the command to serve the build files, specifying the config file
# CMD ["serve", "-s", "build", "-c", "build/serve.json"]
CMD ["serve", "-s", "build"]

# Expose the port the app runs on
EXPOSE 3000