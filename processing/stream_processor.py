import logging

from config.logging_config import setup_logging
from config.settings import get_settings
from database.db import Database
from kafka.consumer import JSONKafkaConsumer
from kafka.producer import JSONKafkaProducer
from processing.feature_engineering import StreamingFeatureEngineer

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    db = Database(settings.database_url)
    producer = JSONKafkaProducer(settings.kafka_bootstrap_servers)
    consumer = JSONKafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=f"{settings.kafka_consumer_group}-processor",
        topics=[settings.kafka_topic_weather, settings.kafka_topic_energy],
    )
    fe = StreamingFeatureEngineer()
    logger.info("stream_processor_started")

    for topic, payload in consumer.messages():
        try:
            db.insert_raw(topic, payload)
            if topic == settings.kafka_topic_weather:
                fe.update_weather(payload)
                logger.info("weather_state_updated")
            elif topic == settings.kafka_topic_energy:
                processed = fe.transform_energy_record(payload)
                db.upsert_processed(processed)
                producer.produce(settings.kafka_topic_processed, key=processed.get("location"), value=processed)
                producer.flush()
                logger.info("processed_record_published", extra={"ctx_event_time": processed["event_time"]})
        except Exception:
            logger.exception("stream_processing_error", extra={"ctx_topic": topic})


if __name__ == "__main__":
    main()
