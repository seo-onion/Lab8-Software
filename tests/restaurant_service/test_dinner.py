import pytest

from restaurant_service.domain.dinner import Dinner, DinnerValidationError

VALID_CARD = "4111111111111111"


def _dinner(**overrides):
    data = {
        "amount": 250.0,
        "card_number": VALID_CARD,
        "restaurant_code": "REST-001",
        "timestamp": "2026-05-30T20:15:00Z",
    }
    data.update(overrides)
    return Dinner(**data)


def test_valid_dinner_is_created():
    dinner = _dinner()

    assert dinner.amount == 250.0
    assert dinner.restaurant_code == "REST-001"


@pytest.mark.parametrize("amount", [0, -1, -100.5])
def test_non_positive_amount_is_rejected(amount):
    with pytest.raises(DinnerValidationError, match="amount"):
        _dinner(amount=amount)


def test_card_number_with_letters_is_rejected():
    with pytest.raises(DinnerValidationError, match="only digits"):
        _dinner(card_number="4111-1111-1111")


@pytest.mark.parametrize("card", ["1234567890", "12345678901234567890"])
def test_card_number_out_of_length_range_is_rejected(card):
    with pytest.raises(DinnerValidationError, match="between"):
        _dinner(card_number=card)


def test_empty_restaurant_code_is_rejected():
    with pytest.raises(DinnerValidationError, match="restaurant_code"):
        _dinner(restaurant_code="   ")


def test_empty_timestamp_is_rejected():
    with pytest.raises(DinnerValidationError, match="timestamp"):
        _dinner(timestamp="")
