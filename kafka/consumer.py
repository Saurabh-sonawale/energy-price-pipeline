import json
import logging
from typing import Dict, Iterable, Iterator, Tuple

from confluent_kafka import Consumer, KafkaException

logger = logging.getLogger(__name__)


class JSONKafkaConsumer:
    """Kafka consumer that yields JSON payload dictionaries."""

    def __init__(self, bootstrap_servers: str, group_id: str, topics: Iterable[str], auto_offset_reset: str = "earliest") -> None:
        self.consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": auto_offset_reset,
                "enable.auto.commit": False,
            }
        )
        self.consumer.subscribe(list(topics))

    def messages(self, timeout: float = 1.0) -> Iterator[Tuple[str, Dict]]:
        while True:
            msg = self.consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            try:
                yield msg.topic(), json.loads(msg.value().decode("utf-8"))
                self.consumer.commit(msg, asynchronous=False)
            except Exception:
                logger.exception("kafka_message_processing_failed", extra={"ctx_topic": msg.topic()})

    def close(self) -> None:
        self.consumer.close()
