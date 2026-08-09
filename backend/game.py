import random
from dataclasses import dataclass, field
from datetime import datetime, timezone

from enums import DISCUSSION_DEFAULT_SECONDS, EARLY_VOTE_DEFAULT_SECONDS, NIGHT_DEFAULT_SECONDS, VOTE_DEFAULT_SECONDS, Faction, Phase
from player import Player
from scenarios import Scenario


def get_role_meta_safe(role_id: str):
    from roles import get_role_meta

    return get_role_meta(role_id)


@dataclass
class NightAction:
    actor_seat: int
    target_seat: int | None
    action_subtype: str | None = None  # e.g. witch: 'heal' | 'poison'
    target_seat_2: int | None = None  # Clairvoyant's 2nd target, Cupid's 2nd link


@dataclass
class TimingRules:
    discussion_seconds: int = DISCUSSION_DEFAULT_SECONDS
    early_vote_after_seconds: int = EARLY_VOTE_DEFAULT_SECONDS
    vote_seconds: int = VOTE_DEFAULT_SECONDS
    night_seconds: int = NIGHT_DEFAULT_SECONDS


@dataclass
class GameState:
    room_code: str
    game_id: str
    scenario: Scenario
    host_seat_id: int
    reveal_on_death: bool = False
    timing: TimingRules = field(default_factory=TimingRules)

    players: dict[int, Player] = field(default_factory=dict)
    phase: Phase = Phase.LOBBY
    round_number: int = 0
    phase_started_at: str | None = None

    submitted_night_actions: dict[int, dict] = field(default_factory=dict)
    submitted_votes: dict[int, int | None] = field(default_factory=dict)
    skip_votes: set[int] = field(default_factory=set)

    pending_effects: dict = field(default_factory=dict)
    wolf_infection_active: bool = False
    winner_faction: str | None = None

    seat_order: list[int] = field(default_factory=list)
    cupid_links: list[tuple[int, int]] = field(default_factory=list)
    twin_pairs: list[tuple[int, int]] = field(default_factory=list)
    cult_members: set[int] = field(default_factory=set)
    vampire_pending_deaths: list[dict] = field(default_factory=list)
    grandmother_seat: int | None = None
    red_hood_seat: int | None = None
    delayed_deaths: dict[int, dict] = field(default_factory=dict)  # seat_id -> {"cause":.., "resolve_round": n}

    def faction_seats(self, faction: Faction) -> list[int]:
        from roles import get_role_meta

        return [
            seat_id
            for seat_id, player in self.players.items()
            if player.is_alive and get_role_meta(player.role_id).faction == faction
        ]

    def alive_seats(self) -> list[int]:
        return [seat_id for seat_id, player in self.players.items() if player.is_alive]

    def assign_roles(self, role_ids: list[str], seats: dict[int, str]) -> None:
        """seats: seat_id -> user_id, display_name already seated in the lobby."""
        from roles import get_role

        shuffled_roles = list(role_ids)
        random.shuffle(shuffled_roles)
        for (seat_id, (user_id, display_name)), role_id in zip(seats.items(), shuffled_roles):
            self.players[seat_id] = Player(
                user_id=user_id,
                seat_id=seat_id,
                display_name=display_name,
                role_id=role_id,
            )
            role_cls = get_role(role_id)
            if role_id == "witch":
                self.players[seat_id].role_state = role_cls.init_state()

        self.seat_order = sorted(self.players.keys())

        twin_seats = [s for s, p in self.players.items() if p.role_id == "twin"]
        if len(twin_seats) == 2:
            self.twin_pairs.append((twin_seats[0], twin_seats[1]))

        grandmother_seats = [s for s, p in self.players.items() if p.role_id == "grandmother"]
        red_hood_seats = [s for s, p in self.players.items() if p.role_id == "red_hood"]
        if grandmother_seats:
            self.grandmother_seat = grandmother_seats[0]
        if red_hood_seats:
            self.red_hood_seat = red_hood_seats[0]

        cult_leader_seats = [s for s, p in self.players.items() if p.role_id == "cult_leader"]
        for seat_id in cult_leader_seats:
            self.cult_members.add(seat_id)

    def start_new_phase(self, phase: Phase) -> None:
        self.phase = phase
        self.phase_started_at = datetime.now(timezone.utc).isoformat()
        if phase == Phase.NIGHT:
            self.submitted_night_actions = {}
        elif phase == Phase.VOTE:
            self.submitted_votes = {}
        elif phase == Phase.DISCUSSION:
            self.skip_votes = set()

    def pending_effects_pop(self, key: str, default):
        return self.pending_effects.pop(key, default)

    def pending_effects_set(self, key: str, value) -> None:
        self.pending_effects[key] = value

    def kill_player(self, seat_id: int, cause: str) -> None:
        player = self.players.get(seat_id)
        if not player or not player.is_alive:
            return
        player.is_alive = False
        player.death_cause = cause
        player.died_on_round = self.round_number

    def check_winner(self) -> str | None:
        alive = set(self.alive_seats())
        if not alive:
            return None

        for seat_a, seat_b in self.twin_pairs:
            if alive == {seat_a, seat_b}:
                return "twins"

        wolves = set(self.faction_seats(Faction.WOLF))
        neutrals = {s for s in alive if get_role_meta_safe(self.players[s].role_id).faction == Faction.NEUTRAL}
        villagers = alive - wolves - neutrals

        lone_wolf_seats = {s for s in wolves if self.players[s].role_id == "lone_wolf"}
        if lone_wolf_seats and wolves == lone_wolf_seats and len(wolves) == 1:
            return "lone_wolf"

        if self.cult_members and alive and alive.issubset(self.cult_members):
            return "cult"

        for solo_role in ("solo_killer", "vampire"):
            solo_seats = {s for s in alive if self.players[s].role_id == solo_role}
            if solo_seats and alive == solo_seats:
                return solo_role

        if not wolves:
            return "villagers"
        if len(wolves) >= len(villagers) + len(neutrals):
            return "wolves"
        return None
