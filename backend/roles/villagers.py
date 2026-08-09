from enums import Faction
from roles.base import Role, RoleMeta


class Villager(Role):
    meta = RoleMeta(
        id="villager", display_name_vi="Dân thường", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Không có kỹ năng đặc biệt. Chỉ thảo luận và bỏ phiếu.",
    )


class Seer(Role):
    meta = RoleMeta(
        id="seer", display_name_vi="Tiên Tri", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=30,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm chọn 1 người, biết được phe của họ.",
    )

    @staticmethod
    def check_faction(game_state, target_seat: int) -> Faction:
        from roles import get_role_meta

        return get_role_meta(game_state.players[target_seat].role_id).faction


class ApprenticeSeer(Role):
    """Dormant until the real Seer dies, then inherits Seer's night action.
    Whether it's 'active' this round is decided by the resolver (checks that
    no living player has role_id == 'seer')."""

    meta = RoleMeta(
        id="apprentice_seer", display_name_vi="Tiên Tri Tập Sự", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=31,
        can_target_self=False, can_target_dead=False,
        description_vi="Ngủ yên cho đến khi Tiên Tri thật chết — kế thừa kỹ năng của Tiên Tri.",
    )

    @staticmethod
    def is_active(game_state) -> bool:
        return not any(p.role_id == "seer" and p.is_alive for p in game_state.players.values())


class MysticSeer(Role):
    meta = RoleMeta(
        id="mystic_seer", display_name_vi="Tiên Tri Bí Ẩn", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=32,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm chọn 1 người, biết chính xác role của họ (không chỉ phe).",
    )


class Clairvoyant(Role):
    meta = RoleMeta(
        id="clairvoyant", display_name_vi="Ngoại Cảm", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=27,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm chọn 2 người, biết 2 người đó có cùng phe không (không biết phe nào).",
    )


class Detective(Role):
    meta = RoleMeta(
        id="detective", display_name_vi="Thám Tử", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=1, priority=28,
        can_target_self=False, can_target_dead=False,
        description_vi="Dùng một lần: biết mục tiêu có phải Sói không.",
    )


class Ghost(Role):
    """Forced dead on night 1 (handled at game start), then lives on in the
    dead-chat channel and may say exactly one word per day in public chat —
    enforced in ws/router.py's day-speak handler via role_state['is_ghost']."""

    meta = RoleMeta(
        id="ghost", display_name_vi="Hồn Ma", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Chết đêm 1; thấy được kênh chat người chết; được nói đúng 1 từ mỗi ngày ở kênh công khai.",
    )


class Guard(Role):
    meta = RoleMeta(
        id="guard", display_name_vi="Bảo Vệ", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=10,
        can_target_self=True, can_target_dead=False,
        description_vi="Mỗi đêm bảo vệ 1 người khỏi bị Sói giết. Không được chọn cùng người 2 đêm liên tiếp.",
    )

    @classmethod
    def valid_targets(cls, game_state, actor_seat: int) -> list[int]:
        targets = super().valid_targets(game_state, actor_seat)
        last_target = game_state.players[actor_seat].role_state.get("last_protected")
        if last_target in targets:
            targets.remove(last_target)
        return targets


class Priest(Role):
    meta = RoleMeta(
        id="priest", display_name_vi="Mục Sư", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=1, priority=12,
        can_target_self=True, can_target_dead=False,
        description_vi="Dùng một lần: làm mục tiêu miễn nhiễm hoàn toàn với đòn Sói (các nguyên nhân chết khác vẫn áp dụng).",
    )


class Witch(Role):
    meta = RoleMeta(
        id="witch", display_name_vi="Phù Thủy", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=25,
        can_target_self=True, can_target_dead=False,
        description_vi="1 bình cứu + 1 bình độc, mỗi bình dùng một lần trong cả ván.",
    )

    @staticmethod
    def init_state() -> dict:
        return {"has_heal_potion": True, "has_poison_potion": True}


class Hunter(Role):
    meta = RoleMeta(
        id="hunter", display_name_vi="Thợ Săn", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=40,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm đánh dấu 1 mục tiêu; nếu Hunter chết, mục tiêu đã đánh dấu chết theo.",
    )


class Huntress(Role):
    meta = RoleMeta(
        id="huntress", display_name_vi="Nữ Thợ Săn", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=1, priority=21,
        can_target_self=False, can_target_dead=False,
        description_vi="Dùng một lần: giết 1 người bất kỳ lúc nào trong đêm.",
    )


class PlagueBearer(Role):
    """Passive: if killed by a wolf bite, the resolver sets
    game_state.wolf_infection_active so wolves miss their next kill vote."""

    meta = RoleMeta(
        id="plague_bearer", display_name_vi="Người Bị Bệnh", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi='Nếu bị Sói giết, Sói bị "lây bệnh" và bỏ qua lượt giết đêm tiếp theo.',
    )


class Cupid(Role):
    meta = RoleMeta(
        id="cupid", display_name_vi="Cupid", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=True, max_uses=1, priority=5,
        can_target_self=True, can_target_dead=False,
        description_vi="Chỉ đêm 1: liên kết 2 người thành cặp đôi — người này chết thì người kia chết theo, bất kể phe.",
    )


class Terrorist(Role):
    """Passive: on death, both seat neighbours (by seat number, wrapping)
    die too — resolved in resolver.py using game_state.seat_order."""

    meta = RoleMeta(
        id="terrorist", display_name_vi="Khủng Bố", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Khi chết, 2 người ngồi cạnh (theo thứ tự ghế) cũng chết theo.",
    )


class Halfbreed(Role):
    meta = RoleMeta(
        id="halfbreed", display_name_vi="Con Lai", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Dân làng thật, nhưng Tiên Tri điều tra thấy là Sói.",
    )


class Cursed(Role):
    """Passive: if hit by a wolf bite, the resolver converts them to
    Werewolf instead of killing them."""

    meta = RoleMeta(
        id="cursed", display_name_vi="Kẻ Bị Nguyền", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Dân làng bình thường; nếu bị Sói cắn, chuyển thành Sói thay vì chết.",
    )


class Clone(Role):
    meta = RoleMeta(
        id="clone", display_name_vi="Nhân Bản", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=True, max_uses=1, priority=6,
        can_target_self=False, can_target_dead=False,
        description_vi="Đêm 1 chọn mục tiêu; nếu mục tiêu chết, kế thừa role của họ.",
    )


class Grandmother(Role):
    meta = RoleMeta(
        id="grandmother", display_name_vi="Bà Ngoại", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Dân làng bình thường, được ghép cặp với Khăn Đỏ.",
    )


class RedHood(Role):
    meta = RoleMeta(
        id="red_hood", display_name_vi="Khăn Đỏ", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Sau khi Bà Ngoại chết, mỗi đêm biết được danh tính của 1 con Sói.",
    )


class Twin(Role):
    meta = RoleMeta(
        id="twin", display_name_vi="Song Sinh", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Nhận ra nhau từ đêm 1; thắng riêng nếu là cặp sống sót cuối cùng.",
    )


class Sorcerer(Role):
    meta = RoleMeta(
        id="sorcerer", display_name_vi="Pháp Sư", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=16,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm im lặng hóa 1 người — hôm sau người đó không được nói (vẫn được bỏ phiếu).",
    )


class OldHag(Role):
    meta = RoleMeta(
        id="old_hag", display_name_vi="Mụ Già", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=14,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm buộc 1 người nghỉ ngày tiếp theo (không nói, không bỏ phiếu).",
    )


class Prince(Role):
    """Passive: immune to the first exile vote against them — resolved in
    vote.py, which reveals the role publicly instead of killing them."""

    meta = RoleMeta(
        id="prince", display_name_vi="Hoàng Tử", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Miễn nhiễm với lần bỏ phiếu trục xuất đầu tiên — bị lật bài công khai thay vì chết.",
    )


class ToughYouth(Role):
    """Passive: a wolf bite on this player is delayed one extra night
    instead of killing immediately — resolved in resolver.py."""

    meta = RoleMeta(
        id="tough_youth", display_name_vi="Thanh Niên Cứng", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi="Nếu bị Sói cắn, chết chậm hơn 1 đêm thay vì ngay lập tức.",
    )


class Gambler(Role):
    meta = RoleMeta(
        id="gambler", display_name_vi="Con Bạc", faction=Faction.VILLAGER,
        acts_at_night=True, first_night_only=False, max_uses=None, priority=20,
        can_target_self=False, can_target_dead=False,
        description_vi="Mỗi đêm (trừ đêm 1): nhắm ngẫu nhiên 1 người — nếu là Sói người đó chết; nếu không, Gambler chết.",
    )


class Drunkard(Role):
    """Passive: from night 2 onward has a random chance each night to
    reroll into a brand-new random role — resolved in resolver.py."""

    meta = RoleMeta(
        id="drunkard", display_name_vi="Bợm Nhậu", faction=Faction.VILLAGER,
        acts_at_night=False, first_night_only=False, max_uses=None, priority=0,
        can_target_self=False, can_target_dead=False,
        description_vi='Dân làng bình thường; từ đêm 2 có xác suất ngẫu nhiên "tỉnh rượu" và nhận role mới ngẫu nhiên.',
    )


VILLAGER_ROLES: dict[str, type[Role]] = {
    "villager": Villager,
    "seer": Seer,
    "apprentice_seer": ApprenticeSeer,
    "mystic_seer": MysticSeer,
    "clairvoyant": Clairvoyant,
    "detective": Detective,
    "ghost": Ghost,
    "guard": Guard,
    "priest": Priest,
    "witch": Witch,
    "hunter": Hunter,
    "huntress": Huntress,
    "plague_bearer": PlagueBearer,
    "cupid": Cupid,
    "terrorist": Terrorist,
    "halfbreed": Halfbreed,
    "cursed": Cursed,
    "clone": Clone,
    "grandmother": Grandmother,
    "red_hood": RedHood,
    "twin": Twin,
    "sorcerer": Sorcerer,
    "old_hag": OldHag,
    "prince": Prince,
    "tough_youth": ToughYouth,
    "gambler": Gambler,
    "drunkard": Drunkard,
}
