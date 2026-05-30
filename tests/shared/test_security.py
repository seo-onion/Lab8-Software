from shared.messaging.security import mask_card_number


def test_masks_all_but_last_four_digits():
    assert mask_card_number("4111111111111111") == "************1111"


def test_short_value_is_fully_masked():
    assert mask_card_number("123") == "***"


def test_value_equal_to_visible_length_is_fully_masked():
    assert mask_card_number("1234") == "****"


def test_none_returns_empty_string():
    assert mask_card_number(None) == ""
