# Use an image that has both Node.js and Python
FROM node:18-bullseye

# Install Python + pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY package*.json ./
COPY requirements.txt ./

# Install dependencies
RUN npm install
RUN pip3 install -r requirements.txt

# Copy rest of your code
COPY . .

# Build Tailwind CSS
RUN npm run build

# Expose port
EXPOSE 8080

# Use gunicorn for production (Railway expects this)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]