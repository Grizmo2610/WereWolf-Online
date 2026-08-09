import os
import sqlite3
from dataclasses import dataclass

from config.settings import settings

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_local_schema() -> None:
    """Create tables in the local SQLite dev DB. No-op when using real D1
    (D1 schema is expected to be applied via wrangler/migrations separately)."""
    if settings.use_d1:
        return
    conn = sqlite3.connect(settings.local_sqlite_path)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


@dataclass
class User:
    id: str
    username: str
    display_name: str
    password_hash: str
    created_at: str


@dataclass
class GameRecord:
    id: str
    room_code: str
    scenario_id: str
    total_players: int
    started_at: str
    ended_at: str | None
    winner_faction: str | None
    status: str
    reveal_on_death: bool


@dataclass
class PlayerRecord:
    id: str
    game_id: str
    user_id: str
    seat_id: int
    role_id: str
    alive_until_round: int | None
    eliminated_by: str | None


@dataclass
class GameSnapshot:
    game_id: str
    room_code: str
    round_number: int
    phase: str
    players: list
    pending_effects: list
    wolf_infection_active: bool
    scenario_id: str
    scenario_custom_rules: dict
    reveal_on_death: bool
    saved_at: str
