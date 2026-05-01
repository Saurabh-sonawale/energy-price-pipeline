from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"
    simulation_mode: bool = True

    openweather_api_key: str = ""
    openweather_city: str = "New York"
    openweather_units: str = "metric"
    gridstatus_api_key: str = ""
    gridstatus_market: str = "nyiso"
    gridstatus_location: str = "NYC"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_weather: str = "weather-data"
    kafka_topic_energy: str = "energy-prices"
    kafka_topic_processed: str = "processed-data"
    kafka_topic_signals: str = "trading-signals"
    kafka_consumer_group: str = "energy-price-pipeline"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "energy_pipeline"
    postgres_user: str = "energy_user"
    postgres_password: str = "energy_password"
    database_url: str = "postgresql://energy_user:energy_password@localhost:5432/energy_pipeline"

    model_path: str = "artifacts/prophet_model.pkl"
    training_lookback_hours: int = 720
    forecast_horizon_hours: int = 24

    buy_threshold: float = 3.0
    sell_threshold: float = 3.0
    max_position_mwh: float = 10.0
    max_daily_trades: int = 20

    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "energy-price-forecasting"


@lru_cache
def get_settings() -> Settings:
    return Settings()
