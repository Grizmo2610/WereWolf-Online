from enums import Faction
from roles.base import Role, RoleMeta


class Fool(Role):
    """Passive: wins alone if exiled specifically by a lynch vote (not by
    any other death cause) — checked in vote.py at the moment of lynch."""

    meta = RoleMeta(
        id="fool", display_name_vi="Kẻ Chán Đời", faction=Faction.NEUTRAL,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Thắng một mình nếu bị trục xuất bằng vote (chỉ nguyên nhân đó mới tính).",
    )


class SoloKiller(Role):
    meta = RoleMeta(
        id="solo_killer", display_name_vi="Sát Nhân Đơn Độc", faction=Faction.NEUTRAL,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=47,
        can_target_self=False, can_target_dead=False,
        description_vi="Giết 1 người/đêm (không phải Sói); thắng khi là người sống sót duy nhất.",
    )


class CultLeader(Role):
    meta = RoleMeta(
        id="cult_leader", display_name_vi="Chủ Giáo Phái", faction=Faction.NEUTRAL,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=49,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm chiêu mộ 1 người vào giáo phái; thắng khi tất cả người sống đều là thành viên.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        targets = super().valid_targets(game_state, actor_seat)
        return [seat for seat in targets if seat not in game_state.cult_members]


class Vampire(Role):
    """Death from Vampire is announced only after the following day's
    discussion ends (the victim stays visibly 'alive' in the interim, but
    is still saveable by Witch/Guard/Priest that same night)."""

    meta = RoleMeta(
        id="vampire", display_name_vi="Ma Cà Rồng", faction=Faction.NEUTRAL,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=48,
        can_target_self=False, can_target_dead=False,
        description_vi="Hút máu 1 người/đêm — cái chết chỉ được công bố sau khi cuộc họp ngày hôm sau kết thúc; vẫn có thể được cứu.",
    )


class Saboteur(Role):
    meta = RoleMeta(
        id="saboteur", display_name_vi="Kẻ Phá Rối", faction=Faction.NEUTRAL,
        acts_at_night=True, first_night_only=False, max_uses=1, priority=8,
        can_target_self=False, can_target_dead=False,
        description_vi="Dùng một lần: hoán đổi role của 2 người ngẫu nhiên.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        # Saboteur picks only ONE seat; the second is chosen at random by
        # the resolver among the remaining alive players.
        return super().valid_targets(game_state, actor_seat)


NEUTRAL_ROLES: dict[str, type[Role]] = {
    "fool": Fool,
    "solo_killer": SoloKiller,
    "cult_leader": CultLeader,
    "vampire": Vampire,
    "saboteur": Saboteur,
}
