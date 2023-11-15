FROM python:3.11.6-bookworm@sha256:99cb81c1d8e4d6fe275c1f5127c770ad86a64286533e06991e1887d3e18aa812

WORKDIR /app

RUN apt update -y && apt install -y autoconf bison flex gcc g++ libnl-route-3-dev libprotobuf-dev libseccomp-dev libtool make pkg-config protobuf-compiler

COPY nsjail/ /nsjail/

RUN cd /nsjail && make && mv /nsjail/nsjail /usr/bin/nsjail && rm -rf /nsjail

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["celery", "-A", "worker", "worker", "--autoscale", "10", "--loglevel", "info"]
