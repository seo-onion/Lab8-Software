from unittest.mock import MagicMock, patch

import pytest
from pika.exceptions import AMQPConnectionError

from restaurant_service.application.ports import PublishError
from restaurant_service.infrastructure.rabbitmq_publisher import (
    RabbitMQDinnerPublisher,
)
from shared.messaging import topology
from shared.messaging.events import DinnerEvent
from shared.messaging.topology import BrokerSettings

EVENT = DinnerEvent(250.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")
SETTINGS = BrokerSettings("localhost", 5672, "students", "secret", "/")


@patch("restaurant_service.infrastructure.rabbitmq_publisher.pika.BlockingConnection")
def test_publish_declares_topology_and_publishes(connection_cls):
    connection = connection_cls.return_value
    channel = connection.channel.return_value

    RabbitMQDinnerPublisher(SETTINGS).publish(EVENT)

    channel.exchange_declare.assert_called_once()
    channel.queue_declare.assert_called_once_with(
        queue=topology.DINNER_QUEUE, durable=True
    )
    channel.queue_bind.assert_called_once()
    channel.basic_publish.assert_called_once()
    _, kwargs = channel.basic_publish.call_args
    assert kwargs["routing_key"] == topology.DINNER_ROUTING_KEY
    assert kwargs["exchange"] == topology.EXCHANGE
    connection.close.assert_called_once()


@patch("restaurant_service.infrastructure.rabbitmq_publisher.pika.BlockingConnection")
def test_publish_closes_connection_even_if_publish_fails(connection_cls):
    connection = connection_cls.return_value
    connection.channel.return_value.basic_publish.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError):
        RabbitMQDinnerPublisher(SETTINGS).publish(EVENT)

    connection.close.assert_called_once()


@patch(
    "restaurant_service.infrastructure.rabbitmq_publisher.pika.BlockingConnection",
    side_effect=AMQPConnectionError("unreachable"),
)
def test_amqp_error_is_wrapped_as_publish_error(_connection_cls):
    with pytest.raises(PublishError, match="could not publish"):
        RabbitMQDinnerPublisher(SETTINGS).publish(EVENT)


@patch("restaurant_service.infrastructure.rabbitmq_publisher.pika.PlainCredentials")
@patch("restaurant_service.infrastructure.rabbitmq_publisher.pika.ConnectionParameters")
@patch("restaurant_service.infrastructure.rabbitmq_publisher.pika.BlockingConnection")
def test_connection_uses_settings(connection_cls, params_cls, creds_cls):
    RabbitMQDinnerPublisher(SETTINGS).publish(EVENT)

    creds_cls.assert_called_once_with("students", "secret")
    _, kwargs = params_cls.call_args
    assert kwargs["host"] == "localhost"
    assert kwargs["port"] == 5672
    assert kwargs["virtual_host"] == "/"
