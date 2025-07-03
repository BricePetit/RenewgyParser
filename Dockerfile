# Dockerfile

# 1. Base Image.
FROM python:3.13-slim

# 2. Set the working directory.
WORKDIR /parser

# 3. Copy the requirements file.
COPY requirements.txt .

# 4. Install the dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the source code and configuration files.
COPY src/ ./src/
COPY ean_config.json .

# 6. Define the entry point.
ENTRYPOINT ["python", "src/renewgy_parser.py"]
