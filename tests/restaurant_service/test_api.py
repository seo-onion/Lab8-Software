import pytest
from fastapi.testclient import TestClient

from restaurant_service.application.ports import DinnerEventPublisher, PublishError
from restaurant_service.application.register_dinner import RegisterDinner
from restaurant_service.infrastructure.api import create_app
from shared.messaging.events import DinnerEvent

VALID_BODY = {
    "amount": 250.0,
    "card_number": "4111111111111111",
    "restaurant_code": "REST-001",
    "timestamp": "2026-05-30T20:15:00Z",
}


class FakePublisher(DinnerEventPublisher):
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.published: list[DinnerEvent] = []

    def publish(self, event: DinnerEvent) -> None:
        if self.fail:
            raise PublishError("broker down")
        self.published.append(event)


def _client(publisher: FakePublisher) -> TestClient:
    return TestClient(create_app(RegisterDinner(publisher)))


def test_post_dinner_returns_202_and_publishes():
    publisher = FakePublisher()
    response = _client(publisher).post("/dinners", json=VALID_BODY)

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "restaurant_code": "REST-001"}
    assert len(publisher.published) == 1


def test_post_dinner_with_invalid_amount_returns_400():
    publisher = FakePublisher()
    body = {**VALID_BODY, "amount": -5}

    response = _client(publisher).post("/dinners", json=body)

    assert response.status_code == 400
    assert publisher.published == []


def test_post_dinner_when_broker_down_returns_503():
    response = _client(FakePublisher(fail=True)).post("/dinners", json=VALID_BODY)

    assert response.status_code == 503


def test_post_dinner_with_missing_field_returns_422():
    body = {"amount": 250.0, "card_number": "4111111111111111"}

    response = _client(FakePublisher()).post("/dinners", json=body)

    assert response.status_code == 422
