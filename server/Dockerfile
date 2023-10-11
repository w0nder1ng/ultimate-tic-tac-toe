FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
