FROM python:3.6-jessie

LABEL maintainer="asd "

WORKDIR /app


# expect a build-time variable
RUN sed -i '/jessie-updates/d' /etc/apt/sources.list \
&&   apt-get update  \
&&   apt-get install -y \
&&   apt-get install -y mysql-client \
&&   apt-get -y install python3-pip \
&&   pip3 install Flask==1.0.2 \
&&   pip3 install numpy==1.15.3 \
&&   pip3 install pandas==0.23.4 \
&&   pip3 install tqdm  \
&&   pip3 install plotly  \
&&   pip3 install clickhouse-driver[lz4]

COPY . /app

CMD python3 /app/main.py
