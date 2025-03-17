import mlflow

from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from mlflow.tracking import MlflowClient

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

def promote_best_model(model_name):
    client = MlflowClient()
    best_accuracy = 0
    best_version = None
    for version in client.search_model_versions(f"name='{model_name}'"):
        tmp_accuracy = version.tags.get("accuracy")
        if tmp_accuracy:
            tmp_accuracy = float(tmp_accuracy)
            if tmp_accuracy>best_accuracy:
                best_accuracy = tmp_accuracy
                best_version = version

    if best_version:
        client.transition_model_version_stage(name = best_version.name, version = best_version.version, stage = "Production")

if __name__ == "__main__":
    train_and_log_model(200, 3)
    train_and_log_model(500, 80)


    promote_best_model("WineApp")