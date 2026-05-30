from rewards_service.application.ports import (
    AccountRepository,
    NotificationPublisher,
    RestaurantRepository,
)
from rewards_service.application.process_dinner import ProcessDinner
from rewards_service.domain.restaurant import Restaurant
from rewards_service.domain.reward import Reward
from shared.messaging.events import DinnerEvent, RewardProcessedEvent

DINNER = DinnerEvent(250.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")


class FakeRestaurantRepository(RestaurantRepository):
    def __init__(self, restaurant: Restaurant | None) -> None:
        self._restaurant = restaurant

    def find(self, code: str) -> Restaurant | None:
        return self._restaurant


class FakeAccountRepository(AccountRepository):
    def __init__(self) -> None:
        self.rewards: list[tuple[str, Reward]] = []

    def add_reward(self, card_number: str, reward: Reward) -> None:
        self.rewards.append((card_number, reward))

    def get_balance(self, card_number: str) -> Reward | None:
        return None


class FakeNotificationPublisher(NotificationPublisher):
    def __init__(self) -> None:
        self.published: list[RewardProcessedEvent] = []

    def publish(self, event: RewardProcessedEvent) -> None:
        self.published.append(event)


def _active(category: str = "premium") -> Restaurant:
    return Restaurant("REST-001", "La Trattoria", category, True)


def test_valid_dinner_updates_account_and_publishes_notification():
    accounts = FakeAccountRepository()
    notifier = FakeNotificationPublisher()
    use_case = ProcessDinner(FakeRestaurantRepository(_active()), accounts, notifier)

    result = use_case.execute(DINNER)

    assert len(accounts.rewards) == 1
    assert accounts.rewards[0][0] == "4111111111111111"
    assert result is not None
    assert notifier.published == [result]
    assert result.points == 25
    assert result.cashback == 12.5


def test_unknown_restaurant_is_discarded():
    accounts = FakeAccountRepository()
    notifier = FakeNotificationPublisher()
    use_case = ProcessDinner(FakeRestaurantRepository(None), accounts, notifier)

    result = use_case.execute(DINNER)

    assert result is None
    assert accounts.rewards == []
    assert notifier.published == []


def test_inactive_restaurant_is_discarded():
    inactive = Restaurant("REST-004", "Antiguo Sabor", "estandar", False)
    accounts = FakeAccountRepository()
    notifier = FakeNotificationPublisher()
    use_case = ProcessDinner(FakeRestaurantRepository(inactive), accounts, notifier)

    result = use_case.execute(DINNER)

    assert result is None
    assert accounts.rewards == []
    assert notifier.published == []


def test_zero_reward_updates_account_but_does_not_notify():
    tiny_dinner = DinnerEvent(0.2, "4111111111111111", "REST-002", "2026-05-30T20:15:00Z")
    accounts = FakeAccountRepository()
    notifier = FakeNotificationPublisher()
    use_case = ProcessDinner(
        FakeRestaurantRepository(_active("estandar")), accounts, notifier
    )

    result = use_case.execute(tiny_dinner)

    assert result is None
    assert len(accounts.rewards) == 1
    assert accounts.rewards[0][1] == Reward(points=0, cashback=0.0)
    assert notifier.published == []
