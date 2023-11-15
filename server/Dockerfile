FROM python:3.11.6-bookworm@sha256:99cb81c1d8e4d6fe275c1f5127c770ad86a64286533e06991e1887d3e18aa812

WORKDIR /app

RUN apt update && apt install -y build-essential rustc

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./entrypoint.sh"]
