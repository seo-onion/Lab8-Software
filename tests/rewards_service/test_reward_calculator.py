import pytest

from rewards_service.domain.restaurant import Restaurant
from rewards_service.domain.reward_calculator import RewardCalculator


def _restaurant(category: str) -> Restaurant:
    return Restaurant(code="REST-001", name="Test", category=category, active=True)


@pytest.fixture
def calculator() -> RewardCalculator:
    return RewardCalculator()


def test_one_point_per_ten_soles(calculator):
    reward = calculator.calculate(250.0, _restaurant("premium"))

    assert reward.points == 25


def test_points_use_floor_division(calculator):
    reward = calculator.calculate(259.9, _restaurant("estandar"))

    assert reward.points == 25


def test_premium_cashback_is_five_percent(calculator):
    reward = calculator.calculate(250.0, _restaurant("premium"))

    assert reward.cashback == 12.5


def test_standard_cashback_is_two_percent(calculator):
    reward = calculator.calculate(250.0, _restaurant("estandar"))

    assert reward.cashback == 5.0


def test_cashback_is_rounded_to_two_decimals(calculator):
    reward = calculator.calculate(33.33, _restaurant("premium"))

    assert reward.cashback == 1.67
