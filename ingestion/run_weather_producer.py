import logging
import time

from config.logging_config import setup_logging
from config.settings import get_settings
from ingestion.weather_client import OpenWeatherClient
from kafka.producer import JSONKafkaProducer

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    client = OpenWeatherClient(
        api_key=settings.openweather_api_key,
        units=settings.openweather_units,
        simulation_mode=settings.simulation_mode,
    )
    producer = JSONKafkaProducer(settings.kafka_bootstrap_servers)
    logger.info("weather_producer_started")
    while True:
        try:
            record = client.fetch_current_weather(settings.openweather_city)
            producer.produce(settings.kafka_topic_weather, key=settings.openweather_city, value=record)
            producer.flush()
            logger.info("weather_record_published", extra={"ctx_topic": settings.kafka_topic_weather})
        except Exception:
            logger.exception("weather_producer_error")
        time.sleep(60)


if __name__ == "__main__":
    main()
