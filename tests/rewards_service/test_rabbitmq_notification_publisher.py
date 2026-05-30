from unittest.mock import patch

import pytest
from pika.exceptions import AMQPConnectionError

from rewards_service.application.ports import PublishError
from rewards_service.infrastructure.rabbitmq_notification_publisher import (
    RabbitMQNotificationPublisher,
)
from shared.messaging import topology
from shared.messaging.events import RewardProcessedEvent
from shared.messaging.topology import BrokerSettings

EVENT = RewardProcessedEvent("4111111111111111", 25, 12.5, "REST-001", "2026-05-30T20:15:01Z")
SETTINGS = BrokerSettings("localhost", 5672, "students", "secret", "/")

_MODULE = "rewards_service.infrastructure.rabbitmq_notification_publisher.pika"


@patch(f"{_MODULE}.BlockingConnection")
def test_publish_sends_to_notification_routing_key(connection_cls):
    channel = connection_cls.return_value.channel.return_value

    RabbitMQNotificationPublisher(SETTINGS).publish(EVENT)

    _, kwargs = channel.basic_publish.call_args
    assert kwargs["routing_key"] == topology.NOTIFICATION_ROUTING_KEY
    assert kwargs["exchange"] == topology.EXCHANGE
    connection_cls.return_value.close.assert_called_once()


@patch(f"{_MODULE}.BlockingConnection", side_effect=AMQPConnectionError("down"))
def test_amqp_error_is_wrapped(_connection_cls):
    with pytest.raises(PublishError, match="could not publish notification"):
        RabbitMQNotificationPublisher(SETTINGS).publish(EVENT)


@patch(f"{_MODULE}.BlockingConnection")
def test_connection_closed_when_publish_fails(connection_cls):
    connection_cls.return_value.channel.return_value.basic_publish.side_effect = (
        RuntimeError("boom")
    )

    with pytest.raises(RuntimeError):
        RabbitMQNotificationPublisher(SETTINGS).publish(EVENT)

    connection_cls.return_value.close.assert_called_once()
