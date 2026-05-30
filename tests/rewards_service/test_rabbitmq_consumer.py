from unittest.mock import MagicMock

from rewards_service.application.ports import PublishError, RepositoryError
from rewards_service.infrastructure.rabbitmq_consumer import DinnerConsumer
from shared.messaging.events import DinnerEvent
from shared.messaging.serialization import serialize
from shared.messaging.topology import BrokerSettings

SETTINGS = BrokerSettings("localhost", 5672, "students", "secret", "/")
EVENT = DinnerEvent(250.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")


def _method():
    method = MagicMock()
    method.delivery_tag = 42
    return method


def test_valid_message_is_processed_and_acked():
    process = MagicMock()
    channel = MagicMock()
    consumer = DinnerConsumer(SETTINGS, process)

    consumer.on_message(channel, _method(), None, serialize(EVENT))

    process.execute.assert_called_once_with(EVENT)
    channel.basic_ack.assert_called_once_with(delivery_tag=42)
    channel.basic_nack.assert_not_called()


def test_malformed_message_is_acked_without_processing():
    process = MagicMock()
    channel = MagicMock()
    consumer = DinnerConsumer(SETTINGS, process)

    consumer.on_message(channel, _method(), None, b"not-json")

    process.execute.assert_not_called()
    channel.basic_ack.assert_called_once_with(delivery_tag=42)


def test_repository_error_triggers_requeue():
    process = MagicMock()
    process.execute.side_effect = RepositoryError("db down")
    channel = MagicMock()

    DinnerConsumer(SETTINGS, process).on_message(channel, _method(), None, serialize(EVENT))

    channel.basic_nack.assert_called_once_with(delivery_tag=42, requeue=True)
    channel.basic_ack.assert_not_called()


def test_publish_error_triggers_requeue():
    process = MagicMock()
    process.execute.side_effect = PublishError("broker down")
    channel = MagicMock()

    DinnerConsumer(SETTINGS, process).on_message(channel, _method(), None, serialize(EVENT))

    channel.basic_nack.assert_called_once_with(delivery_tag=42, requeue=True)
