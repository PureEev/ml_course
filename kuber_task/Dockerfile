FROM apache/airflow:2.7.2

USER root
RUN apt-get update && \
    apt-get install -y python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt