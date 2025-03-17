#!/bin/bash

# Инициализация базы данных Airflow
airflow db init

# Создание пользователя Airflow
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com

# Запуск MLflow tracking server
mlflow server \
    --backend-store-uri sqlite:////opt/airflow/mlflow_tracking/mlflow.db \
    --default-artifact-root /opt/airflow/mlflow_tracking/artifacts \
    --host 0.0.0.0 \
    --port 5001 &

# Запуск Flask приложения через Gunicorn
gunicorn --chdir /opt/airflow/flask_app \
    --bind :5000 \
    --workers 2 \
    --timeout 300 \
    app:app &

# Запуск Airflow webserver и scheduler
airflow webserver & airflow scheduler