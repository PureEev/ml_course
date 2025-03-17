from airflow import DAG
from datetime import datetime, timedelta

import mlflow

from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from mlflow.tracking import MlflowClient

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

mlflow.set_tracking_uri('http://localhost:5000')


def train_and_log_model(n_estimators, max_depth):
    data = load_wine()
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    with mlflow.start_run():
        #mlflow.log_param('n_estimators', n_estimators)
        #mlflow.log_param('max_depth', max_depth)
        mlflow.autolog()
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=42,
            max_depth=max_depth,
            n_jobs=-1
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        mlflow.log_metric('accuracy', accuracy)

        run_id = mlflow.active_run().info.run_id

        model_uri = f"runs:/{run_id}/wine-app"
        registered_model = mlflow.register_model(model_uri, "WineApp")

        client = MlflowClient()
        client.set_model_version_tag(name = "WineApp", version=registered_model.version, key = 'accuracy', value = str(round(accuracy, 3)))

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes = 5)
}

with DAG(
    "ml_pipeline",
    default_args = default_args,
    schedule_interval= "@weekly",

) as dag:
    train_task = PythonOperator(
        task_id='train_and_log_model',
        python_callable=train_and_log_model,
        dag=dag
    ),

    build_image_task = BashOperator(
        task_id = 'build_docker_image',
        bash_command= 'docker build -t pureev7/wine-model-app:latest . && docker tag pureev7/wine-model-app:latest wine-model-app:latest && docker push wine-model-app:latest',
        dag=dag
    )

    deploy_to_k8s_task = BashOperator(
        task_id = 'deploy_to_k8s',
        bash_command = 'kubectl apply -f deployment.yaml && kubectl apply -f service.yaml && kubectl apply -f ingress.yaml',
        dag=dag
    )

    train_task >> build_image_task >> deploy_to_k8s_task