# Hardened Python Environment (CIS Level 2)
FROM python:3.11-slim

# Create a non-root user with no login shell
RUN useradd -m -s /usr/sbin/nologin galleyuser

WORKDIR /app

# Copy dependency manifest first for better layer caching
COPY requirements.txt .

# Install dependencies as root, then drop privileges
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Pre-generate visual assets inside the image
RUN python src/asset_gen.py

# Run as non-root user
USER galleyuser

EXPOSE 5000

CMD ["python", "src/server.py"]
