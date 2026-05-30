import pytest

from shared.messaging.events import DinnerEvent
from shared.messaging.serialization import (
    SerializationError,
    deserialize,
    serialize,
)


def test_serialize_then_deserialize_returns_equivalent_event():
    event = DinnerEvent(250.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")

    payload = serialize(event)
    restored = deserialize(payload, DinnerEvent)

    assert restored == event


def test_serialize_produces_utf8_json_bytes():
    event = DinnerEvent(10.0, "4111111111111111", "REST-001", "2026-05-30T20:15:00Z")

    payload = serialize(event)

    assert isinstance(payload, bytes)
    assert b"REST-001" in payload


def test_deserialize_invalid_json_raises_serialization_error():
    with pytest.raises(SerializationError):
        deserialize(b"not-json", DinnerEvent)


def test_deserialize_missing_field_raises_serialization_error():
    with pytest.raises(SerializationError):
        deserialize(b'{"amount": 10.0}', DinnerEvent)
