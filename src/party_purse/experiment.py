import mlflow


def run_experiment(param1: int = 10):
    with mlflow.start_run():
        mlflow.log_param("param1", param1)

        result = param1 * 2

        mlflow.log_metric("result", result)

        print(f"Result: {result}")
