"""Reward calculation rules (RN-01, RN-02)."""

from __future__ import annotations

from rewards_service.domain.restaurant import Restaurant
from rewards_service.domain.reward import Reward

# RN-01: 1 point per S/ 10 consumed.
SOLES_PER_POINT = 10
# RN-02: cashback rate by restaurant category.
PREMIUM_CASHBACK_RATE = 0.05
STANDARD_CASHBACK_RATE = 0.02


class RewardCalculator:
    """Calculates the reward for a dinner based on its amount and restaurant."""

    def calculate(self, amount: float, restaurant: Restaurant) -> Reward:
        points = int(amount // SOLES_PER_POINT)
        rate = PREMIUM_CASHBACK_RATE if restaurant.is_premium else STANDARD_CASHBACK_RATE
        cashback = round(amount * rate, 2)
        return Reward(points=points, cashback=cashback)
