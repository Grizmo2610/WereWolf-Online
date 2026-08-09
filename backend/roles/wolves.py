from enums import Faction
from roles.base import Role, RoleMeta


class Werewolf(Role):
    meta = RoleMeta(
        id="werewolf", display_name_vi="Sói", faction=Faction.WOLF,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Thấy đồng đội Sói từ đêm 1. Mỗi đêm cùng vote chọn 1 mục tiêu cắn.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        targets = super().valid_targets(game_state, actor_seat)
        wolf_seats = game_state.faction_seats(Faction.WOLF)
        return [seat for seat in targets if seat not in wolf_seats]


class AlphaWolf(Role):
    """Once per game: convert the target to Werewolf instead of killing
    them (fails silently if the target is guarded/immune that night)."""

    meta = RoleMeta(
        id="alpha_wolf", display_name_vi="Sói Đầu Đàn", faction=Faction.WOLF,
        acts_at_night=True, first_night_only=False, max_uses=1, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Một lần/ván: chuyển mục tiêu thành Sói thay vì giết; vô hiệu nếu mục tiêu đang được bảo vệ.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        return Werewolf.valid_targets(game_state, actor_seat)


class WolfCub(Role):
    """Passive: on death, the village gets to lynch 2 people the following
    day instead of 1 — resolved in vote.py."""

    meta = RoleMeta(
        id="wolf_cub", display_name_vi="Sói Con", faction=Faction.WOLF,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Khi chết, ngày hôm sau được phép trục xuất 2 người thay vì 1.",
    )


class LoneWolf(Role):
    """Acts like a normal Werewolf but carries a separate win condition:
    wins alone once it's the last wolf standing — checked in game.check_winner."""

    meta = RoleMeta(
        id="lone_wolf", display_name_vi="Sói Cô Độc", faction=Faction.WOLF,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Hoạt động như Sói thường nhưng có điều kiện thắng riêng: là con Sói cuối cùng còn sống.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        return Werewolf.valid_targets(game_state, actor_seat)


class VegetarianWolf(Role):
    """Doesn't take part in the kill vote, but still wins with the wolf
    faction — simply has no night action."""

    meta = RoleMeta(
        id="vegetarian_wolf", display_name_vi="Sói Ăn Chay", faction=Faction.WOLF,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Không tham gia vote giết; vẫn thắng cùng phe Sói.",
    )


class WolfSeer(Role):
    meta = RoleMeta(
        id="wolf_seer", display_name_vi="Sói Tiên Tri", faction=Faction.WOLF,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=33,
        can_target_self=False, can_target_dead=False,
        description_vi="Sói có kỹ năng điều tra phe như Tiên Tri.",
    )


class Medium(Role):
    """Dormant (no wolf-chat, no vote) unless the real Seer dies — then
    becomes a Wolf Seer. Activity gated the same way as ApprenticeSeer."""

    meta = RoleMeta(
        id="medium", display_name_vi="Bà Đồng", faction=Faction.WOLF,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=34,
        can_target_self=False, can_target_dead=False,
        description_vi="Không thức cùng đàn; bí mật theo dõi Tiên Tri — trở thành Sói Tiên Tri nếu Tiên Tri thật chết.",
    )

    @staticmethod
    def is_active(game_state) -> bool:
        from roles.villagers import ApprenticeSeer

        return ApprenticeSeer.is_active(game_state)


WOLF_ROLES: dict[str, type[Role]] = {
    "werewolf": Werewolf,
    "alpha_wolf": AlphaWolf,
    "wolf_cub": WolfCub,
    "lone_wolf": LoneWolf,
    "vegetarian_wolf": VegetarianWolf,
    "wolf_seer": WolfSeer,
    "medium": Medium,
}
