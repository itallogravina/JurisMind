FROM python:3.11-slim

# System deps: poppler for pdf2image, libreoffice for DOCX→PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Volumes for user data
VOLUME ["/app/inputs", "/app/outputs"]

EXPOSE 8501

HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
