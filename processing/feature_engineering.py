from collections import deque
from datetime import datetime
from statistics import mean, pstdev
from typing import Any, Deque, Dict, Optional

import pandas as pd


class StreamingFeatureEngineer:
    """Stateful feature engineering for streaming market and weather observations."""

    def __init__(self, history_size: int = 48, anomaly_zscore_threshold: float = 3.0) -> None:
        self.price_history: Deque[float] = deque(maxlen=history_size)
        self.latest_weather: Dict[str, Any] = {}
        self.anomaly_zscore_threshold = anomaly_zscore_threshold

    def update_weather(self, weather: Dict[str, Any]) -> None:
        self.latest_weather = weather

    def transform_energy_record(self, energy: Dict[str, Any]) -> Dict[str, Any]:
        price = float(energy["price_mwh"])
        event_time = pd.to_datetime(energy["event_time"], utc=True)

        record = {
            "event_time": event_time.isoformat(),
            "market": energy.get("market"),
            "location": energy.get("location"),
            "price_mwh": price,
            "demand_mw": _safe_float(energy.get("demand_mw")),
            "fuel_mix_gas_pct": _safe_float(energy.get("fuel_mix_gas_pct")),
            "temperature": _safe_float(self.latest_weather.get("temperature")),
            "humidity": _safe_float(self.latest_weather.get("humidity")),
            "wind_speed": _safe_float(self.latest_weather.get("wind_speed")),
            "price_lag_1": self._lag(1),
            "price_lag_3": self._lag(3),
            "price_rolling_3": self._rolling(3),
            "price_rolling_24": self._rolling(24),
            "hour": int(event_time.hour),
            "day_of_week": int(event_time.dayofweek),
            "week_of_year": int(event_time.isocalendar().week),
            "is_weekend": int(event_time.dayofweek >= 5),
            "is_anomaly": self._is_anomaly(price),
        }
        self.price_history.append(price)
        return record

    def _lag(self, periods: int) -> Optional[float]:
        if len(self.price_history) >= periods:
            return list(self.price_history)[-periods]
        return None

    def _rolling(self, window: int) -> Optional[float]:
        if len(self.price_history) >= window:
            values = list(self.price_history)[-window:]
            return float(sum(values) / len(values))
        if self.price_history:
            values = list(self.price_history)
            return float(sum(values) / len(values))
        return None

    def _is_anomaly(self, price: float) -> bool:
        if len(self.price_history) < 12:
            return False
        values = list(self.price_history)
        std = pstdev(values)
        if std == 0:
            return False
        z_score = abs((price - mean(values)) / std)
        return z_score >= self.anomaly_zscore_threshold


def build_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare processed records for Prophet training."""
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"])
    frame = df.copy()
    frame["event_time"] = pd.to_datetime(frame["event_time"], utc=True).dt.tz_convert(None)
    frame = frame.sort_values("event_time")
    frame["price_mwh"] = frame["price_mwh"].ffill().bfill()
    frame = frame.rename(columns={"event_time": "ds", "price_mwh": "y"})
    return frame[["ds", "y"]].dropna()


def _safe_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
