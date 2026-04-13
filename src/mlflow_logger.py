import mlflow
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def setup_mlflow():
    mlflow.set_tracking_uri(config["mlflow"]["tracking_uri"])
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

def log_ocr_run(params: dict, metrics: dict, artifacts: list = None):
    """Log a run to MLflow."""
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        if artifacts:
            for artifact in artifacts:
                mlflow.log_artifact(artifact) 