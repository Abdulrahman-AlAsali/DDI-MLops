# app/Dockerfile
FROM python:3.10
WORKDIR /app

COPY app_requirements.txt .
RUN pip install --no-cache-dir -r app_requirements.txt

COPY . .

EXPOSE 80

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
