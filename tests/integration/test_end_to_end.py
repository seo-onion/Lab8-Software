"""End-to-end integration of the full flow without a live broker.

An in-memory broker double carries the *serialized* bytes between stages, so the
real serialization contract (shared), the use cases and the real SQLite
repositories are all exercised together:

    RegisterDinner -> [dinner queue] -> DinnerConsumer/ProcessDinner -> SQLite
                                     -> [notification queue] -> Notifier
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from restaurant_service.application.ports import DinnerEventPublisher
from restaurant_service.application.register_dinner import (
    RegisterDinner,
    RegisterDinnerCommand,
)
from rewards_service.application.ports import NotificationPublisher
from rewards_service.application.process_dinner import ProcessDinner
from rewards_service.domain.reward import Reward
from rewards_service.infrastructure.database import init_db
from rewards_service.infrastructure.notifier import Notifier
from rewards_service.infrastructure.rabbitmq_consumer import DinnerConsumer
from rewards_service.infrastructure.sqlite_account_repository import (
    SqliteAccountRepository,
)
from rewards_service.infrastructure.sqlite_restaurant_repository import (
    SqliteRestaurantRepository,
)
from shared.messaging.events import DinnerEvent, RewardProcessedEvent
from shared.messaging.serialization import serialize
from shared.messaging.topology import BrokerSettings

SETTINGS = BrokerSettings("localhost", 5672, "students", "secret", "/")
CARD = "4111111111111111"


class InMemoryQueue:
    """Holds serialized message bytes, mimicking a broker queue."""

    def __init__(self) -> None:
        self.messages: list[bytes] = []


class QueuingDinnerPublisher(DinnerEventPublisher):
    """Producer-side publisher that drops serialized events into a queue."""

    def __init__(self, queue: InMemoryQueue) -> None:
        self._queue = queue

    def publish(self, event: DinnerEvent) -> None:
        self._queue.messages.append(serialize(event))


class QueuingNotificationPublisher(NotificationPublisher):
    """Rewards-side publisher that drops serialized notifications into a queue."""

    def __init__(self, queue: InMemoryQueue) -> None:
        self._queue = queue

    def publish(self, event: RewardProcessedEvent) -> None:
        self._queue.messages.append(serialize(event))


def _drain(queue: InMemoryQueue, handler) -> None:
    """Deliver every queued message to a consumer's ``on_message`` handler."""
    while queue.messages:
        body = queue.messages.pop(0)
        method = MagicMock()
        method.delivery_tag = 1
        channel = MagicMock()
        handler(channel, method, None, body)


@pytest.fixture
def db_path(tmp_path) -> str:
    path = str(tmp_path / "rewards.db")
    init_db(path)
    return path


def test_full_flow_credits_account_and_notifies(db_path, caplog):
    dinner_queue = InMemoryQueue()
    notification_queue = InMemoryQueue()

    register = RegisterDinner(QueuingDinnerPublisher(dinner_queue))
    accounts = SqliteAccountRepository(db_path)
    consumer = DinnerConsumer(
        SETTINGS,
        ProcessDinner(
            restaurants=SqliteRestaurantRepository(db_path),
            accounts=accounts,
            notifications=QueuingNotificationPublisher(notification_queue),
        ),
    )
    notifier = Notifier(SETTINGS)

    # 1. Producer registers a S/250 dinner at a premium restaurant.
    register.execute(
        RegisterDinnerCommand(250.0, CARD, "REST-001", "2026-05-30T20:15:00Z")
    )
    assert len(dinner_queue.messages) == 1

    # 2. Rewards consumer processes the dinner -> updates account + notifies.
    _drain(dinner_queue, consumer.on_message)
    assert accounts.get_balance(CARD) == Reward(points=25, cashback=12.5)
    assert len(notification_queue.messages) == 1

    # 3. Notifier delivers the notification (masked card in the log).
    import logging

    with caplog.at_level(logging.INFO):
        _drain(notification_queue, notifier.on_message)
    assert "************1111" in caplog.text
    assert CARD not in caplog.text


def test_full_flow_for_inactive_restaurant_is_discarded(db_path):
    dinner_queue = InMemoryQueue()
    notification_queue = InMemoryQueue()

    register = RegisterDinner(QueuingDinnerPublisher(dinner_queue))
    accounts = SqliteAccountRepository(db_path)
    consumer = DinnerConsumer(
        SETTINGS,
        ProcessDinner(
            restaurants=SqliteRestaurantRepository(db_path),
            accounts=accounts,
            notifications=QueuingNotificationPublisher(notification_queue),
        ),
    )

    # REST-004 is seeded as inactive.
    register.execute(
        RegisterDinnerCommand(250.0, CARD, "REST-004", "2026-05-30T20:15:00Z")
    )
    _drain(dinner_queue, consumer.on_message)

    assert accounts.get_balance(CARD) is None
    assert notification_queue.messages == []


def test_two_dinners_accumulate_rewards(db_path):
    dinner_queue = InMemoryQueue()
    notification_queue = InMemoryQueue()

    register = RegisterDinner(QueuingDinnerPublisher(dinner_queue))
    accounts = SqliteAccountRepository(db_path)
    consumer = DinnerConsumer(
        SETTINGS,
        ProcessDinner(
            restaurants=SqliteRestaurantRepository(db_path),
            accounts=accounts,
            notifications=QueuingNotificationPublisher(notification_queue),
        ),
    )

    register.execute(
        RegisterDinnerCommand(250.0, CARD, "REST-001", "2026-05-30T20:15:00Z")
    )
    register.execute(
        RegisterDinnerCommand(100.0, CARD, "REST-002", "2026-05-30T21:00:00Z")
    )
    _drain(dinner_queue, consumer.on_message)

    # REST-001 premium: 25 pts + 12.5 cashback; REST-002 standard: 10 pts + 2.0
    assert accounts.get_balance(CARD) == Reward(points=35, cashback=14.5)
    assert len(notification_queue.messages) == 2
