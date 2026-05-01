"""Optional Airflow DAG for scheduled retraining and dashboard export.

Place this file in your Airflow DAGs folder if you use Airflow instead of cron.
"""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="energy_price_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["energy", "forecasting", "mlops"],
) as dag:
    retrain = BashOperator(
        task_id="daily_model_retraining",
        bash_command="cd /opt/energy-price-pipeline && docker compose --profile batch run --rm model-trainer",
    )

    export = BashOperator(
        task_id="export_tableau_csv",
        bash_command="cd /opt/energy-price-pipeline && docker compose --profile batch run --rm dashboard-export",
    )

    retrain >> export
