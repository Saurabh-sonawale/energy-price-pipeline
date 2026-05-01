import json
import logging
from typing import Any, Dict, Optional

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class JSONKafkaProducer:
    """Kafka producer that serializes dictionaries as UTF-8 JSON."""

    def __init__(self, bootstrap_servers: str) -> None:
        self.producer = Producer({"bootstrap.servers": bootstrap_servers, "enable.idempotence": True})

    @staticmethod
    def _delivery_report(err, msg) -> None:
        if err is not None:
            logger.error("kafka_delivery_failed", extra={"ctx_error": str(err), "ctx_topic": msg.topic() if msg else None})
        else:
            logger.debug("kafka_delivery_succeeded", extra={"ctx_topic": msg.topic(), "ctx_partition": msg.partition()})

    def produce(self, topic: str, key: Optional[str], value: Dict[str, Any]) -> None:
        payload = json.dumps(value, default=str).encode("utf-8")
        self.producer.produce(topic=topic, key=key, value=payload, callback=self._delivery_report)
        self.producer.poll(0)

    def flush(self) -> None:
        self.producer.flush()
