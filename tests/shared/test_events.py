from shared.messaging.events import DinnerEvent, RewardProcessedEvent


def test_dinner_event_round_trips_through_dict():
    event = DinnerEvent(
        amount=250.0,
        card_number="4111111111111111",
        restaurant_code="REST-001",
        timestamp="2026-05-30T20:15:00Z",
    )

    assert DinnerEvent.from_dict(event.to_dict()) == event


def test_dinner_event_to_dict_has_expected_keys():
    event = DinnerEvent(10.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")

    assert event.to_dict() == {
        "amount": 10.0,
        "card_number": "4111111111111111",
        "restaurant_code": "REST-001",
        "timestamp": "2026-05-30T20:15:00Z",
    }


def test_reward_processed_event_round_trips_through_dict():
    event = RewardProcessedEvent(
        card_number="4111111111111111",
        points=25,
        cashback=12.5,
        restaurant_code="REST-001",
        timestamp="2026-05-30T20:15:01Z",
    )

    assert RewardProcessedEvent.from_dict(event.to_dict()) == event
