from dataclasses import dataclass, field


@dataclass
class Player:
    user_id: str
    seat_id: int
    display_name: str
    role_id: str
    is_alive: bool = True
    is_afk: bool = False
    is_connected: bool = True
    # role-specific mutable state (potions left, last protected target, etc).
    # Never stored on the Role class itself — a Role class instance/type can
    # be shared across multiple players (e.g. several Werewolf seats).
    role_state: dict = field(default_factory=dict)
    death_cause: str | None = None
    died_on_round: int | None = None
