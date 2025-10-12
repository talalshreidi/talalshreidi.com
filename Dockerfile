# Use a Node + Python base image
FROM node:18-bullseye

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY package*.json ./
COPY requirements.txt ./

# Install Node and Python dependencies
RUN npm install
RUN pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Build Tailwind assets
RUN npm run build

# Expose the port your app runs on 
EXPOSE 5000

# Run your Python web app (adjust the command if your entry file differs)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
