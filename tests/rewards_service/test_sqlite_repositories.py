import pytest

from rewards_service.application.ports import RepositoryError
from rewards_service.domain.reward import Reward
from rewards_service.infrastructure.database import init_db
from rewards_service.infrastructure.sqlite_account_repository import (
    SqliteAccountRepository,
)
from rewards_service.infrastructure.sqlite_restaurant_repository import (
    SqliteRestaurantRepository,
)

CARD = "4111111111111111"


@pytest.fixture
def db_path(tmp_path) -> str:
    path = str(tmp_path / "rewards.db")
    init_db(path)
    return path


def test_seeded_active_restaurant_is_found(db_path):
    repo = SqliteRestaurantRepository(db_path)

    restaurant = repo.find("REST-001")

    assert restaurant is not None
    assert restaurant.is_premium is True
    assert restaurant.active is True


def test_seeded_inactive_restaurant_is_inactive(db_path):
    restaurant = SqliteRestaurantRepository(db_path).find("REST-004")

    assert restaurant is not None
    assert restaurant.active is False


def test_unknown_restaurant_returns_none(db_path):
    assert SqliteRestaurantRepository(db_path).find("REST-999") is None


def test_init_db_is_idempotent(db_path):
    init_db(db_path)  # second call must not fail nor duplicate

    assert SqliteRestaurantRepository(db_path).find("REST-001") is not None


def test_balance_is_none_for_unknown_account(db_path):
    assert SqliteAccountRepository(db_path).get_balance(CARD) is None


def test_add_reward_creates_account(db_path):
    repo = SqliteAccountRepository(db_path)

    repo.add_reward(CARD, Reward(points=25, cashback=12.5))

    assert repo.get_balance(CARD) == Reward(points=25, cashback=12.5)


def test_add_reward_accumulates(db_path):
    repo = SqliteAccountRepository(db_path)

    repo.add_reward(CARD, Reward(points=25, cashback=12.5))
    repo.add_reward(CARD, Reward(points=10, cashback=4.0))

    assert repo.get_balance(CARD) == Reward(points=35, cashback=16.5)


def test_repository_error_on_missing_schema(tmp_path):
    path = str(tmp_path / "empty.db")  # never initialized -> no tables

    with pytest.raises(RepositoryError):
        SqliteRestaurantRepository(path).find("REST-001")

    with pytest.raises(RepositoryError):
        SqliteAccountRepository(path).get_balance(CARD)

    with pytest.raises(RepositoryError):
        SqliteAccountRepository(path).add_reward(CARD, Reward(1, 1.0))
