from shared.messaging import topology
from shared.messaging.topology import BrokerSettings


def test_broker_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5673")
    monkeypatch.setenv("RABBITMQ_USER", "tester")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "secret")
    monkeypatch.setenv("RABBITMQ_VHOST", "/test")

    settings = BrokerSettings.from_env()

    assert settings == BrokerSettings(
        host="localhost",
        port=5673,
        user="tester",
        password="secret",
        virtual_host="/test",
    )


def test_broker_settings_use_defaults_when_env_absent(monkeypatch):
    for var in (
        "RABBITMQ_HOST",
        "RABBITMQ_PORT",
        "RABBITMQ_USER",
        "RABBITMQ_PASSWORD",
        "RABBITMQ_VHOST",
    ):
        monkeypatch.delenv(var, raising=False)

    settings = BrokerSettings.from_env()

    assert settings.host == "213.199.42.57"
    assert settings.port == 5672
    assert settings.user == "students"
    assert settings.password == ""
    assert settings.virtual_host == "/"


def test_topology_names_are_unique_per_team():
    assert topology.EXCHANGE.endswith("_Sebastian_Hernandez_t1")
    assert topology.DINNER_QUEUE.endswith("_Sebastian_Hernandez_t1")
    assert topology.NOTIFICATION_QUEUE.endswith("_Sebastian_Hernandez_t1")
    assert topology.DINNER_ROUTING_KEY == "cena.registrada"
    assert topology.NOTIFICATION_ROUTING_KEY == "recompensa.procesada"
