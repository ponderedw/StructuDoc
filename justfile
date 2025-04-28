local:
  docker compose down
  docker compose up --build


local_all:
  docker build -f base.Dockerfile . -t hipposysai/base_structudoc:latest
  docker compose down
  docker compose up --build


prod:
  docker compose -f docker-compose-prod.yml down
  docker compose -f docker-compose-prod.yml pull
  docker compose -f docker-compose-prod.yml up --build


prod_image:
  docker build -f base.Dockerfile . -t hipposysai/base_structudoc:latest
  docker push hipposysai/base_structudoc:latest
  docker build . -t hipposysai/structudoc:latest
  docker push hipposysai/structudoc:latest