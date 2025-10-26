FROM pondered/base_structudoc:latest

COPY ./fastapi ./
COPY streamlit ./streamlit
COPY docker-bootstrap.sh ./

# Set execute permissions
RUN chmod +x ./docker-bootstrap.sh
