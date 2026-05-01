import json
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Iterator, List, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class Database:
    """Thin database utility layer for inserts and analytic queries."""

    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(database_url, pool_pre_ping=True, future=True)

    @contextmanager
    def begin(self) -> Iterator[Any]:
        with self.engine.begin() as conn:
            yield conn

    def insert_raw(self, topic: str, payload: Dict[str, Any]) -> None:
        event_time = payload.get("event_time")
        source = payload.get("source", "unknown")
        with self.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO raw_data(source, topic, event_time, payload)
                    VALUES (:source, :topic, :event_time, CAST(:payload AS JSONB))
                    """
                ),
                {"source": source, "topic": topic, "event_time": event_time, "payload": json.dumps(payload, default=str)},
            )

    def upsert_processed(self, record: Dict[str, Any]) -> None:
        columns = [
            "event_time", "market", "location", "price_mwh", "demand_mw", "fuel_mix_gas_pct",
            "temperature", "humidity", "wind_speed", "price_lag_1", "price_lag_3", "price_rolling_3",
            "price_rolling_24", "hour", "day_of_week", "week_of_year", "is_weekend", "is_anomaly",
        ]
        values = {col: record.get(col) for col in columns}
        assignments = ", ".join([f"{col}=EXCLUDED.{col}" for col in columns if col != "event_time"])
        sql = f"""
            INSERT INTO processed_data({', '.join(columns)})
            VALUES ({', '.join(':' + col for col in columns)})
            ON CONFLICT(event_time) DO UPDATE SET {assignments}
        """
        with self.begin() as conn:
            conn.execute(text(sql), values)

    def insert_forecast(self, forecast: Dict[str, Any]) -> None:
        with self.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO forecasts(forecast_time, yhat, yhat_lower, yhat_upper, model_version)
                    VALUES (:forecast_time, :yhat, :yhat_lower, :yhat_upper, :model_version)
                    """
                ),
                forecast,
            )

    def insert_signal(self, signal: Dict[str, Any]) -> None:
        with self.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO trading_signals(event_time, actual_price, forecast_price, signal, position_mwh, reason)
                    VALUES (:event_time, :actual_price, :forecast_price, :signal, :position_mwh, :reason)
                    """
                ),
                signal,
            )

    def load_processed_frame(self, limit: Optional[int] = None) -> pd.DataFrame:
        sql = "SELECT * FROM processed_data ORDER BY event_time"
        if limit:
            sql = f"SELECT * FROM processed_data ORDER BY event_time DESC LIMIT {int(limit)}"
        return pd.read_sql(sql, self.engine).sort_values("event_time")

    def read_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        return pd.read_sql(text(sql), self.engine, params=params)
