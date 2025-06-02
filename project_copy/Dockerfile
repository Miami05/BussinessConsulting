FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install packages using only pre-built wheels where possible
RUN pip install --upgrade pip && \
    pip install --only-binary=all --no-cache-dir \
        Flask \
        flasgger \
        python-dotenv \
        cohere \
        prometheus_flask_exporter \
        prometheus_client \
        pandas \
        "Werkzeug==2.3.7" \
        "numpy==1.24.3" \
        "scikit-learn==1.3" || \
    pip install --no-cache-dir -r requirements.txt

# Install trimesh separately as it might need compilation
RUN pip install --no-cache-dir "trimesh==3.23.5"

# Copy the rest of the application
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
