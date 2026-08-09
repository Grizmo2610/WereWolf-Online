import random
import string
import uuid

import psutil

from config.settings import settings

from game import GameState
from scenarios import get_scenario
from seat import Seat

RAM_THRESHOLD_PERCENT = 80
CPU_THRESHOLD_PERCENT = 85
ROOM_CODE_LENGTH = 6


def can_accept_connection() -> bool:
    if settings.env != "production":
        return True  # no load-shedding in dev — always accept
    ram_ok = psutil.virtual_memory().percent < RAM_THRESHOLD_PERCENT
    cpu_ok = psutil.cpu_percent(interval=0.1) < CPU_THRESHOLD_PERCENT
    return ram_ok and cpu_ok


SERVER_OVERLOAD_MESSAGE = (
    "Server đang thở hổn hển vì dev chưa nạp thẻ 💸 Vui lòng thử lại sau vài phút "
    "— đang cố thuyết phục con server tội nghiệp này gắng thêm một chút nữa 🙏"
)
SERVER_OVERLOAD_MESSAGE_SHORT = "Dev đang broke nên server chỉ có vậy thôi 🥲 Thử lại sau nhé!"


class Room:
    def __init__(self, room_code: str, host_user_id: str, host_display_name: str, scenario_id: str):
        self.room_code = room_code
        self.scenario = get_scenario(scenario_id)
        self.seats: dict[int, Seat] = {1: Seat(seat_id=1, user_id=host_user_id, display_name=host_display_name, is_ready=False)}
        self.host_seat_id = 1
        self.game_state: GameState | None = None
        self.runner = None
        self.status = "waiting"
        self.reveal_on_death = False
        self.timing_overrides: dict = {}  # keys: discussion_seconds, early_vote_after_seconds, vote_seconds, night_seconds

    def add_player(self, user_id: str, display_name: str) -> int:
        if len(self.seats) >= self.scenario.max_players:
            raise ValueError("Phòng đã đầy")
        next_seat_id = max(self.seats.keys(), default=0) + 1
        self.seats[next_seat_id] = Seat(seat_id=next_seat_id, user_id=user_id, display_name=display_name)
        return next_seat_id

    def remove_player(self, seat_id: int) -> None:
        self.seats.pop(seat_id, None)
        if seat_id == self.host_seat_id and self.seats:
            self.host_seat_id = min(self.seats.keys())

    def all_ready(self) -> bool:
        return all(seat.is_ready for seat in self.seats.values())

    def can_start(self) -> bool:
        return self.all_ready() and len(self.seats) >= self.scenario.min_players

    def settings_payload(self) -> dict:
        from enums import (
            DISCUSSION_DEFAULT_SECONDS,
            EARLY_VOTE_DEFAULT_SECONDS,
            NIGHT_DEFAULT_SECONDS,
            VOTE_DEFAULT_SECONDS,
        )

        defaults = {
            "discussion_seconds": DISCUSSION_DEFAULT_SECONDS,
            "early_vote_after_seconds": EARLY_VOTE_DEFAULT_SECONDS,
            "vote_seconds": VOTE_DEFAULT_SECONDS,
            "night_seconds": NIGHT_DEFAULT_SECONDS,
        }
        return {
            "reveal_on_death": self.reveal_on_death,
            **{key: self.timing_overrides.get(key, default) for key, default in defaults.items()},
        }

    def update_settings(self, payload: dict) -> None:
        from enums import (
            DISCUSSION_MAX_SECONDS,
            DISCUSSION_MIN_SECONDS,
            EARLY_VOTE_MIN_SECONDS,
            NIGHT_MAX_SECONDS,
            NIGHT_MIN_SECONDS,
            VOTE_MAX_SECONDS,
            VOTE_MIN_SECONDS,
        )

        bounds = {
            "discussion_seconds": (DISCUSSION_MIN_SECONDS, DISCUSSION_MAX_SECONDS),
            "early_vote_after_seconds": (EARLY_VOTE_MIN_SECONDS, DISCUSSION_MAX_SECONDS),
            "vote_seconds": (VOTE_MIN_SECONDS, VOTE_MAX_SECONDS),
            "night_seconds": (NIGHT_MIN_SECONDS, NIGHT_MAX_SECONDS),
        }
        if "reveal_on_death" in payload:
            self.reveal_on_death = bool(payload["reveal_on_death"])
        for key, (lo, hi) in bounds.items():
            if key in payload:
                try:
                    value = int(payload[key])
                except (TypeError, ValueError):
                    continue
                self.timing_overrides[key] = max(lo, min(hi, value))


class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}

    def create_room(self, host_user_id: str, host_display_name: str, scenario_id: str) -> Room:
        room_code = self._generate_room_code()
        room = Room(room_code, host_user_id, host_display_name, scenario_id)
        self._rooms[room_code] = room
        return room

    def get_room(self, room_code: str) -> Room | None:
        return self._rooms.get(room_code)

    def delete_room(self, room_code: str) -> None:
        self._rooms.pop(room_code, None)

    def _generate_room_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(alphabet, k=ROOM_CODE_LENGTH))
            if code not in self._rooms:
                return code


room_manager = RoomManager()
