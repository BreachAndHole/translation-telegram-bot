FROM python:3.10-alpine3.15

WORKDIR /app

COPY requirements.txt requirements.txt

RUN set -ex \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . .

CMD ["python3", "main.py"]
