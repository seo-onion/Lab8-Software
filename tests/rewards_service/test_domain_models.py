from rewards_service.domain.restaurant import Restaurant
from rewards_service.domain.reward import Reward


def test_premium_restaurant_is_premium():
    assert Restaurant("R", "N", "premium", True).is_premium is True


def test_standard_restaurant_is_not_premium():
    assert Restaurant("R", "N", "estandar", True).is_premium is False


def test_reward_with_points_is_positive():
    assert Reward(points=1, cashback=0.0).is_positive is True


def test_reward_with_cashback_is_positive():
    assert Reward(points=0, cashback=0.5).is_positive is True


def test_empty_reward_is_not_positive():
    assert Reward(points=0, cashback=0.0).is_positive is False
