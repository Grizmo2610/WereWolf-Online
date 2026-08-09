from dataclasses import dataclass

from enums import Faction


@dataclass(frozen=True)
class RoleMeta:
    id: str
    display_name_vi: str
    faction: Faction
    acts_at_night: bool
    first_night_only: bool
    max_uses: int | None
    priority: int
    can_target_self: bool
    can_target_dead: bool
    description_vi: str


class Role:
    meta: RoleMeta

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        """Seats this role may target tonight. Base rule: alive seats,
        excluding self unless can_target_self, excluding dead unless
        can_target_dead. Subclasses narrow further (e.g. wolves excluding
        wolves)."""
        targets = []
        for seat_id, player in game_state.players.items():
            if seat_id == actor_seat and not cls.meta.can_target_self:
                continue
            if not player.is_alive and not cls.meta.can_target_dead:
                continue
            targets.append(seat_id)
        return targets
