import uuid
from collections import Counter

from enums import Faction, Phase
from game import GameState, TimingRules
from roles import get_role_meta
from scenarios import ScenarioFiller
from ws import events as ev
from ws.broadcaster import broadcaster


async def start_game(room) -> None:
    role_ids = ScenarioFiller.fill(room.scenario, len(room.seats))

    game_state = GameState(
        room_code=room.room_code,
        game_id=str(uuid.uuid4()),
        scenario=room.scenario,
        host_seat_id=room.host_seat_id,
        reveal_on_death=room.reveal_on_death,
        timing=TimingRules(
            discussion_seconds=room.timing_overrides.get("discussion_seconds", TimingRules().discussion_seconds),
            early_vote_after_seconds=room.timing_overrides.get(
                "early_vote_after_seconds", TimingRules().early_vote_after_seconds
            ),
            vote_seconds=room.timing_overrides.get("vote_seconds", TimingRules().vote_seconds),
            night_seconds=room.timing_overrides.get("night_seconds", TimingRules().night_seconds),
        ),
    )
    seats_for_assign = {
        seat_id: (seat.user_id, seat.display_name) for seat_id, seat in room.seats.items()
    }
    game_state.assign_roles(role_ids, seats_for_assign)
    _apply_ghost_forced_death(game_state)
    room.game_state = game_state
    room.status = "in_progress"

    await _broadcast_game_start_info(game_state)
    await _send_private_role_info(game_state)


def _apply_ghost_forced_death(gs: GameState) -> None:
    for player in gs.players.values():
        if player.role_id == "ghost":
            player.is_alive = False
            player.death_cause = "ghost_fate"
            player.died_on_round = 1
            player.role_state["is_ghost"] = True


async def _broadcast_game_start_info(gs: GameState) -> None:
    role_counts = Counter(p.role_id for p in gs.players.values())
    faction_counts = Counter(get_role_meta(p.role_id).faction.value for p in gs.players.values())
    role_descriptions = {
        role_id: get_role_meta(role_id).description_vi for role_id in role_counts
    }
    await broadcaster.broadcast(
        gs.room_code,
        ev.GAME_START,
        {
            "total_players": len(gs.players),
            "role_counts": dict(role_counts),
            "faction_counts": dict(faction_counts),
            "timing_rules": {
                "discussion_seconds": gs.timing.discussion_seconds,
                "early_vote_after_seconds": gs.timing.early_vote_after_seconds,
                "vote_seconds": gs.timing.vote_seconds,
                "night_seconds": gs.timing.night_seconds,
            },
            "role_descriptions": role_descriptions,
        },
    )


async def _send_private_role_info(gs: GameState) -> None:
    wolf_seats = gs.faction_seats(Faction.WOLF)
    for seat_id, player in gs.players.items():
        role_meta = get_role_meta(player.role_id)
        await broadcaster.send_to_seat(
            gs.room_code,
            seat_id,
            ev.ROLE_ASSIGNED,
            {
                "role_id": player.role_id,
                "role_meta": {
                    "display_name_vi": role_meta.display_name_vi,
                    "faction": role_meta.faction.value,
                    "description_vi": role_meta.description_vi,
                },
                "ally_info": None,
            },
        )

    for seat_id in wolf_seats:
        await broadcaster.send_to_seat(gs.room_code, seat_id, ev.WOLF_SEATS, {"wolf_seat_ids": wolf_seats})
