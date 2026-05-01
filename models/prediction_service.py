import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config.logging_config import setup_logging
from config.settings import get_settings
from database.db import Database
from kafka.consumer import JSONKafkaConsumer
from kafka.producer import JSONKafkaProducer
from models.model_utils import load_model
from trading.strategy import TradingStrategy

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    db = Database(settings.database_url)
    producer = JSONKafkaProducer(settings.kafka_bootstrap_servers)
    consumer = JSONKafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=f"{settings.kafka_consumer_group}-prediction",
        topics=[settings.kafka_topic_processed],
        auto_offset_reset="latest",
    )
    strategy = TradingStrategy(
        buy_threshold=settings.buy_threshold,
        sell_threshold=settings.sell_threshold,
        max_position_mwh=settings.max_position_mwh,
        max_daily_trades=settings.max_daily_trades,
    )
    logger.info("prediction_service_started")

    for _, processed in consumer.messages():
        try:
            if not Path(settings.model_path).exists():
                logger.warning("model_missing_waiting", extra={"ctx_model_path": settings.model_path})
                time.sleep(10)
                continue

            model = load_model(settings.model_path)
            event_time = pd.to_datetime(processed["event_time"], utc=True).tz_convert(None)
            forecast = model.predict(pd.DataFrame({"ds": [event_time]})).iloc[0]
            forecast_record = {
                "forecast_time": event_time.isoformat(),
                "yhat": float(forecast["yhat"]),
                "yhat_lower": float(forecast.get("yhat_lower", forecast["yhat"])),
                "yhat_upper": float(forecast.get("yhat_upper", forecast["yhat"])),
                "model_version": "prophet-local",
            }
            db.insert_forecast(forecast_record)

            signal = strategy.generate_signal(
                event_time=processed["event_time"],
                actual_price=float(processed["price_mwh"]),
                forecast_price=float(forecast_record["yhat"]),
            )
            db.insert_signal(signal)
            producer.produce(settings.kafka_topic_signals, key=signal["signal"], value=signal)
            producer.flush()
            logger.info("signal_published", extra={"ctx_signal": signal["signal"]})
        except Exception:
            logger.exception("prediction_service_error")


if __name__ == "__main__":
    main()
