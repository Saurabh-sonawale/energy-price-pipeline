import logging
import time

from config.logging_config import setup_logging
from config.settings import get_settings
from ingestion.gridstatus_client import GridStatusClient
from kafka.producer import JSONKafkaProducer

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    client = GridStatusClient(api_key=settings.gridstatus_api_key, simulation_mode=settings.simulation_mode)
    producer = JSONKafkaProducer(settings.kafka_bootstrap_servers)
    logger.info("energy_producer_started")
    while True:
        try:
            record = client.fetch_latest_price(settings.gridstatus_market, settings.gridstatus_location)
            producer.produce(settings.kafka_topic_energy, key=settings.gridstatus_location, value=record)
            producer.flush()
            logger.info("energy_record_published", extra={"ctx_topic": settings.kafka_topic_energy})
        except Exception:
            logger.exception("energy_producer_error")
        time.sleep(60)


if __name__ == "__main__":
    main()
