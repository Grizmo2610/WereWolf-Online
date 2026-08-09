from dataclasses import dataclass


@dataclass
class Seat:
    seat_id: int
    user_id: str | None = None
    display_name: str | None = None
    is_ready: bool = False
    is_connected: bool = True
