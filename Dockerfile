FROM python:3.13-alpine

WORKDIR /app

COPY server.py /app/server.py

ENV SERVICE_HOST=0.0.0.0
ENV SERVICE_PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]

