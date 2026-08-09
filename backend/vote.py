from enums import SKIP_DISCUSSION_RATIO, DeathCause
from game import GameState


def tally_votes(votes: dict[int, int | None]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for target_seat in votes.values():
        if target_seat is None:
            continue
        counts[target_seat] = counts.get(target_seat, 0) + 1
    return counts


def top_voted_seats(votes: dict[int, int | None], exclude: set[int] | None = None) -> list[int]:
    exclude = exclude or set()
    counts = {seat: c for seat, c in tally_votes(votes).items() if seat not in exclude}
    if not counts:
        return []
    max_votes = max(counts.values())
    top = [seat for seat, count in counts.items() if count == max_votes]
    return top if len(top) == 1 else []


def resolve_vote(game_state: GameState) -> dict:
    """Returns {"deaths": [...], "winner_faction": str|None}.
    Handles Prince immunity (revealed instead of killed, once), Fool's
    solo win if lynched, and Wolf Cub's death granting a double-lynch the
    following day."""
    lynch_count = game_state.pending_effects_pop("double_lynch_count", 1)
    already_lynched: set[int] = set()
    deaths: list[dict] = []
    winner_faction = None

    for _ in range(lynch_count):
        top = top_voted_seats(game_state.submitted_votes, exclude=already_lynched)
        if not top:
            break
        seat_id = top[0]
        already_lynched.add(seat_id)
        player = game_state.players[seat_id]

        if player.role_id == "prince" and not player.role_state.get("immunity_used"):
            player.role_state["immunity_used"] = True
            deaths.append({"seat_id": seat_id, "cause": "prince_immunity", "revealed_only": True})
            continue

        game_state.kill_player(seat_id, DeathCause.LYNCH.value)
        deaths.append({"seat_id": seat_id, "cause": DeathCause.LYNCH.value})

        if player.role_id == "fool":
            winner_faction = "fool"
        if player.role_id == "wolf_cub":
            game_state.pending_effects_set("double_lynch_count", 2)

    return {"deaths": deaths, "winner_faction": winner_faction}


def skip_discussion_threshold_met(game_state: GameState) -> bool:
    alive_count = len(game_state.alive_seats())
    if alive_count == 0:
        return False
    return len(game_state.skip_votes) / alive_count > SKIP_DISCUSSION_RATIO
