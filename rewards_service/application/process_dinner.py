"""Use case: process a dinner event into a reward (CU-02)."""

from __future__ import annotations

from rewards_service.application.ports import (
    AccountRepository,
    NotificationPublisher,
    RestaurantRepository,
)
from rewards_service.domain.reward_calculator import RewardCalculator
from shared.messaging.events import DinnerEvent, RewardProcessedEvent


class ProcessDinner:
    """Validates the restaurant, calculates the reward and updates the account."""

    def __init__(
        self,
        restaurants: RestaurantRepository,
        accounts: AccountRepository,
        notifications: NotificationPublisher,
        calculator: RewardCalculator | None = None,
    ) -> None:
        self._restaurants = restaurants
        self._accounts = accounts
        self._notifications = notifications
        self._calculator = calculator or RewardCalculator()

    def execute(self, event: DinnerEvent) -> RewardProcessedEvent | None:
        """Process the dinner. Returns the notification event, or ``None`` if
        the dinner was discarded (RN-04) or yielded no reward (RN-07).
        """
        restaurant = self._restaurants.find(event.restaurant_code)
        if restaurant is None or not restaurant.active:
            return None

        reward = self._calculator.calculate(event.amount, restaurant)
        self._accounts.add_reward(event.card_number, reward)

        if not reward.is_positive:
            return None

        notification = RewardProcessedEvent(
            card_number=event.card_number,
            points=reward.points,
            cashback=reward.cashback,
            restaurant_code=event.restaurant_code,
            timestamp=event.timestamp,
        )
        self._notifications.publish(notification)
        return notification
