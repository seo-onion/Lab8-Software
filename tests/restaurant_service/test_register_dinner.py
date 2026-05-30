import pytest

from restaurant_service.application.ports import DinnerEventPublisher, PublishError
from restaurant_service.application.register_dinner import (
    RegisterDinner,
    RegisterDinnerCommand,
)
from restaurant_service.domain.dinner import DinnerValidationError
from shared.messaging.events import DinnerEvent


class FakePublisher(DinnerEventPublisher):
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.published: list[DinnerEvent] = []

    def publish(self, event: DinnerEvent) -> None:
        if self.fail:
            raise PublishError("broker down")
        self.published.append(event)


def _command(**overrides) -> RegisterDinnerCommand:
    data = {
        "amount": 250.0,
        "card_number": "4111111111111111",
        "restaurant_code": "REST-001",
        "timestamp": "2026-05-30T20:15:00Z",
    }
    data.update(overrides)
    return RegisterDinnerCommand(**data)


def test_valid_command_publishes_event_and_returns_it():
    publisher = FakePublisher()
    use_case = RegisterDinner(publisher)

    event = use_case.execute(_command())

    assert publisher.published == [event]
    assert event.restaurant_code == "REST-001"
    assert event.amount == 250.0


def test_invalid_command_does_not_publish():
    publisher = FakePublisher()
    use_case = RegisterDinner(publisher)

    with pytest.raises(DinnerValidationError):
        use_case.execute(_command(amount=0))

    assert publisher.published == []


def test_publish_error_propagates():
    use_case = RegisterDinner(FakePublisher(fail=True))

    with pytest.raises(PublishError):
        use_case.execute(_command())
