from enums import Faction
from game import GameState, NightAction
from roles import get_role_meta

WOLF_BITE_ROLE_IDS = {"werewolf", "lone_wolf"}


def tier1_actions_by_priority(game_state: GameState, actions: list[NightAction]) -> list[NightAction]:
    non_bite_actions = [
        a for a in actions if game_state.players[a.actor_seat].role_id not in WOLF_BITE_ROLE_IDS
    ]
    return sorted(
        non_bite_actions,
        key=lambda a: get_role_meta(game_state.players[a.actor_seat].role_id).priority,
    )


def tally_wolf_votes(game_state: GameState, actions: list[NightAction]) -> int | None:
    votes: dict[int, int] = {}
    for action in actions:
        role_id = game_state.players[action.actor_seat].role_id
        if role_id not in WOLF_BITE_ROLE_IDS or action.target_seat is None:
            continue
        votes[action.target_seat] = votes.get(action.target_seat, 0) + 1

    if not votes:
        return None

    max_votes = max(votes.values())
    top_targets = [seat for seat, count in votes.items() if count == max_votes]
    return top_targets[0] if len(top_targets) == 1 else None
