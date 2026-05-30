"""Entry point of the restaurant service (producer)."""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from restaurant_service.application.register_dinner import RegisterDinner
from restaurant_service.infrastructure.api import create_app
from restaurant_service.infrastructure.rabbitmq_publisher import (
    RabbitMQDinnerPublisher,
)
from shared.messaging.topology import BrokerSettings

load_dotenv()
logging.basicConfig(level=logging.INFO)

publisher = RabbitMQDinnerPublisher(BrokerSettings.from_env())
app = create_app(RegisterDinner(publisher))


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
