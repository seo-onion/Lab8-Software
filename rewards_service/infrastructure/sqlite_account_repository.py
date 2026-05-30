"""SQLite implementation of ``AccountRepository`` (accumulates rewards)."""

from __future__ import annotations

import sqlite3

from rewards_service.application.ports import AccountRepository, RepositoryError
from rewards_service.domain.reward import Reward
from rewards_service.infrastructure.database import connect


class SqliteAccountRepository(AccountRepository):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def add_reward(self, card_number: str, reward: Reward) -> None:
        try:
            connection = connect(self._db_path)
            try:
                connection.execute(
                    "INSERT INTO accounts "
                    "(card_number, total_points, total_cashback) "
                    "VALUES (?, ?, ?) "
                    "ON CONFLICT(card_number) DO UPDATE SET "
                    "total_points = total_points + excluded.total_points, "
                    "total_cashback = total_cashback + excluded.total_cashback",
                    (card_number, reward.points, reward.cashback),
                )
                connection.commit()
            finally:
                connection.close()
        except sqlite3.Error as exc:
            raise RepositoryError(f"could not update account: {exc}") from exc

    def get_balance(self, card_number: str) -> Reward | None:
        try:
            connection = connect(self._db_path)
            try:
                row = connection.execute(
                    "SELECT total_points, total_cashback "
                    "FROM accounts WHERE card_number = ?",
                    (card_number,),
                ).fetchone()
            finally:
                connection.close()
        except sqlite3.Error as exc:
            raise RepositoryError(f"could not query account: {exc}") from exc

        if row is None:
            return None
        return Reward(points=row[0], cashback=row[1])
