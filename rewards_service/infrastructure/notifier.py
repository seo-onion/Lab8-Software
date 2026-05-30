"""Notifier: consumes ``recompensa.procesada`` and simulates the delivery (CU-03).

The notification is simulated by logging it (with the card number masked); no
real email/SMS provider is contacted.
"""

from __future__ import annotations

import logging

import pika

from shared.messaging import topology
from shared.messaging.events import RewardProcessedEvent
from shared.messaging.security import mask_card_number
from shared.messaging.serialization import SerializationError, deserialize
from shared.messaging.topology import BrokerSettings

logger = logging.getLogger(__name__)


class Notifier:
    """Consumes reward notifications and simulates sending them to the customer."""

    def __init__(self, settings: BrokerSettings) -> None:
        self._settings = settings

    def on_message(self, channel, method, _properties, body: bytes) -> None:
        """Handle one notification: deserialize, simulate delivery, acknowledge."""
        try:
            event = deserialize(body, RewardProcessedEvent)
        except SerializationError:
            logger.warning("Discarding malformed notification message")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        logger.info(
            "Notification sent to customer card=%s: +%s points, +%.2f cashback",
            mask_card_number(event.card_number),
            event.points,
            event.cashback,
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self) -> None:  # pragma: no cover - requires a live broker
        connection = pika.BlockingConnection(self._connection_parameters())
        channel = connection.channel()
        channel.exchange_declare(
            exchange=topology.EXCHANGE,
            exchange_type=topology.EXCHANGE_TYPE,
            durable=True,
        )
        channel.queue_declare(queue=topology.NOTIFICATION_QUEUE, durable=True)
        channel.queue_bind(
            queue=topology.NOTIFICATION_QUEUE,
            exchange=topology.EXCHANGE,
            routing_key=topology.NOTIFICATION_ROUTING_KEY,
        )
        channel.basic_consume(
            queue=topology.NOTIFICATION_QUEUE, on_message_callback=self.on_message
        )
        logger.info("Waiting for reward notifications. Press CTRL+C to exit.")
        channel.start_consuming()

    def _connection_parameters(self) -> pika.ConnectionParameters:  # pragma: no cover
        credentials = pika.PlainCredentials(
            self._settings.user, self._settings.password
        )
        return pika.ConnectionParameters(
            host=self._settings.host,
            port=self._settings.port,
            virtual_host=self._settings.virtual_host,
            credentials=credentials,
        )
