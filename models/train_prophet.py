import logging
import os
from datetime import datetime, timezone

import mlflow
import pandas as pd
from prophet import Prophet

from config.logging_config import setup_logging
from config.settings import get_settings
from database.db import Database
from models.model_utils import regression_metrics, save_model
from processing.feature_engineering import build_training_frame

logger = logging.getLogger(__name__)


def train() -> dict:
    settings = get_settings()
    setup_logging(settings.log_level)
    db = Database(settings.database_url)
    raw_df = db.load_processed_frame(limit=settings.training_lookback_hours)
    train_df = build_training_frame(raw_df)

    if len(train_df) < 48:
        raise ValueError("At least 48 processed records are recommended before training Prophet.")

    split_idx = max(int(len(train_df) * 0.8), len(train_df) - 24)
    train_part = train_df.iloc[:split_idx]
    valid_part = train_df.iloc[split_idx:]

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    with mlflow.start_run(run_name=f"prophet-{datetime.now(timezone.utc).isoformat()}"):
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
            seasonality_mode="additive",
        )
        model.fit(train_part)
        validation_forecast = model.predict(valid_part[["ds"]])
        metrics = regression_metrics(valid_part["y"], validation_forecast["yhat"])

        save_model(model, settings.model_path)
        mlflow.log_param("model", "Prophet")
        mlflow.log_param("rows", len(train_df))
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(settings.model_path)

        # Save decomposition sample for dashboards/notebooks.
        future = model.make_future_dataframe(periods=settings.forecast_horizon_hours, freq="h")
        full_forecast = model.predict(future)
        os.makedirs("artifacts", exist_ok=True)
        full_forecast[["ds", "yhat", "trend", "daily", "weekly"]].tail(200).to_csv(
            "artifacts/forecast_components.csv", index=False
        )
        mlflow.log_artifact("artifacts/forecast_components.csv")

    logger.info("model_trained", extra={"ctx_mae": metrics["mae"], "ctx_rmse": metrics["rmse"]})
    return metrics


if __name__ == "__main__":
    print(train())
