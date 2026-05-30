import logging
from unittest.mock import MagicMock

from rewards_service.infrastructure.notifier import Notifier
from shared.messaging.events import RewardProcessedEvent
from shared.messaging.serialization import serialize
from shared.messaging.topology import BrokerSettings

SETTINGS = BrokerSettings("localhost", 5672, "students", "secret", "/")
EVENT = RewardProcessedEvent("4111111111111111", 25, 12.5, "REST-001", "2026-05-30T20:15:01Z")


def _method():
    method = MagicMock()
    method.delivery_tag = 7
    return method


def test_notification_is_logged_with_masked_card_and_acked(caplog):
    channel = MagicMock()

    with caplog.at_level(logging.INFO):
        Notifier(SETTINGS).on_message(channel, _method(), None, serialize(EVENT))

    assert "************1111" in caplog.text
    assert "4111111111111111" not in caplog.text
    channel.basic_ack.assert_called_once_with(delivery_tag=7)


def test_malformed_notification_is_acked():
    channel = MagicMock()

    Notifier(SETTINGS).on_message(channel, _method(), None, b"broken")

    channel.basic_ack.assert_called_once_with(delivery_tag=7)
