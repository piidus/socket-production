# Define version variable (replace with your actual version)
#ENV VERSION=0.0.1

# Stage 1: Build environment for installing dependencies
FROM python:3.12-alpine AS builder

WORKDIR /app

# Copy requirements.txt (if you have one)
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy main script and log settings
COPY server.py log_settings.py /app/

# Stage 2: Production image (slim)
FROM python:3.12-alpine

WORKDIR /app

# Copy only server.py and log_settings.py from builder stage
COPY --from=builder /app/server.py /app/log_settings.py ./

# Expose port (if you have one)
EXPOSE 12345 
#(adjust if your application uses a different port)

# Entrypoint with version information (replace with your usage)
CMD ["python", "server.py", "--version", "$VERSION"]
