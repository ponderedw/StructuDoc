FROM python:3.12-slim

WORKDIR /app

# Combine package installation and cleanup in one RUN to reduce layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pandoc \
    # Instead of full texlive, install only what you need
    texlive-xetex \
    texlive-fonts-recommended \
    # Consider if you really need fonts-extra (it's very large)
    # texlive-fonts-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY ./fastapi/requirements.txt ./fastapi-requirements.txt
COPY streamlit/requirments.txt ./streamlit-requirements.txt

# Fix typo in filename (requirments -> requirements)
# Install all requirements in one step to reduce layers
RUN pip install --no-cache-dir -r fastapi-requirements.txt \
    && pip install --no-cache-dir -r streamlit-requirements.txt \
    # Clean pip cache
    && pip cache purge

