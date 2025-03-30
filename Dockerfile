FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js, ExifTool, and FFmpeg
RUN apt-get update && apt-get install -y \
    curl \
    perl \
    libimage-exiftool-perl \
    ffmpeg \
	tk \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary directories and files
COPY code/ ./code
COPY supplementary_files/ ./supplementary_files
COPY node_modules/ ./node_modules
COPY gfam_exec.py gfam_gui.py package-lock.json ./

# Install JavaScript dependencies if node_modules is missing (optional fallback)
RUN if [ ! -d "node_modules" ]; then npm install; fi

# Install Python dependencies
RUN pip install --no-cache-dir numpy pandas

# Set executable permissions for scripts
RUN chmod +x gfam_exec.py gfam_gui.py

# Update PATH for supplementary files (if your scripts require it)
ENV PATH="/app/supplementary_files:${PATH}"

# Default command shows basic usage info
CMD ["python", "gfam_exec.py", "--help"]
