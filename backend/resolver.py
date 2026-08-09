import random

from enums import DeathCause, Faction
from game import GameState, NightAction
from night_order import tally_wolf_votes, tier1_actions_by_priority
from roles import get_role_meta

RANDOM_ROLE_TARGET_SUBTYPE = "random"
DRUNKARD_SOBER_UP_CHANCE = 0.15


def resolve_night(game_state: GameState, actions: list[NightAction]) -> tuple[list[dict], dict[int, dict]]:
    by_role = _index_actions_by_role(game_state, actions)
    info: dict[int, dict] = {}

    _apply_cupid(game_state, by_role)
    _apply_clone(game_state, by_role)
    _apply_saboteur(game_state, by_role)

    protected = _collect_protection(game_state, by_role)
    kills: dict[int, str] = {}
    converts: dict[int, str] = {}

    _apply_wolf_bite(game_state, actions, protected, kills, converts)
    _apply_alpha_wolf(game_state, by_role, protected, converts)
    _apply_gambler(game_state, by_role, kills)
    _apply_huntress(game_state, by_role, kills)
    _apply_witch(game_state, by_role, kills)
    _apply_solo_killer(game_state, by_role, kills)
    _apply_vampire(game_state, by_role)
    _apply_cult_leader(game_state, by_role)
    _apply_hunter_mark(game_state, by_role)

    _gather_info(game_state, by_role, info)

    _apply_converts(game_state, converts)
    _resolve_delayed_deaths(game_state, kills)
    _apply_hunter_counter_kill(game_state, kills)
    _apply_cupid_chain(game_state, kills)
    _apply_terrorist_chain(game_state, kills)
    _apply_clone_inheritance(game_state, kills)
    _apply_drunkard_reroll(game_state)

    deaths = _apply_deaths(game_state, kills)
    return deaths, info


def _index_actions_by_role(game_state: GameState, actions: list[NightAction]) -> dict[str, list[NightAction]]:
    by_role: dict[str, list[NightAction]] = {}
    for action in actions:
        role_id = game_state.players[action.actor_seat].role_id
        by_role.setdefault(role_id, []).append(action)
    return by_role


def _apply_cupid(game_state: GameState, by_role: dict) -> None:
    for action in by_role.get("cupid", []):
        if action.target_seat is not None and action.target_seat_2 is not None:
            game_state.cupid_links.append((action.target_seat, action.target_seat_2))


def _apply_clone(game_state: GameState, by_role: dict) -> None:
    for action in by_role.get("clone", []):
        if action.target_seat is not None:
            game_state.players[action.actor_seat].role_state["clone_target"] = action.target_seat


def _apply_saboteur(game_state: GameState, by_role: dict) -> None:
    for action in by_role.get("saboteur", []):
        actor = game_state.players[action.actor_seat]
        if actor.role_state.get("used") or action.target_seat is None:
            continue
        candidates = [s for s in game_state.alive_seats() if s not in (action.actor_seat, action.target_seat)]
        if not candidates:
            continue
        other_seat = random.choice(candidates)
        seat_a, seat_b = action.target_seat, other_seat
        game_state.players[seat_a].role_id, game_state.players[seat_b].role_id = (
            game_state.players[seat_b].role_id,
            game_state.players[seat_a].role_id,
        )
        actor.role_state["used"] = True


def _collect_protection(game_state: GameState, by_role: dict) -> set[int]:
    protected: set[int] = set()
    for action in by_role.get("guard", []):
        if action.target_seat is not None:
            protected.add(action.target_seat)
            game_state.players[action.actor_seat].role_state["last_protected"] = action.target_seat
    for action in by_role.get("priest", []):
        actor = game_state.players[action.actor_seat]
        if action.target_seat is not None and not actor.role_state.get("used"):
            protected.add(action.target_seat)
            actor.role_state["used"] = True
    return protected


def _apply_wolf_bite(game_state, actions, protected, kills, converts) -> None:
    if game_state.wolf_infection_active:
        game_state.wolf_infection_active = False  # Plague Bearer: wolves skip this night's bite
        return
    wolf_target = tally_wolf_votes(game_state, actions)
    if wolf_target is None or wolf_target in protected:
        return
    target_player = game_state.players[wolf_target]
    if target_player.role_id == "cursed":
        converts[wolf_target] = "werewolf"
    elif target_player.role_id == "tough_youth" and not target_player.role_state.get("bitten_once"):
        target_player.role_state["bitten_once"] = True
        game_state.delayed_deaths[wolf_target] = {
            "cause": DeathCause.WOLF_BITE.value, "resolve_round": game_state.round_number + 1
        }
    else:
        kills[wolf_target] = DeathCause.WOLF_BITE.value
        if target_player.role_id == "plague_bearer":
            game_state.wolf_infection_active = True


def _apply_alpha_wolf(game_state, by_role, protected, converts) -> None:
    for action in by_role.get("alpha_wolf", []):
        actor = game_state.players[action.actor_seat]
        if actor.role_state.get("used") or action.target_seat is None:
            continue
        if action.target_seat in protected:
            continue
        converts[action.target_seat] = "werewolf"
        actor.role_state["used"] = True


def _apply_gambler(game_state, by_role, kills) -> None:
    for action in by_role.get("gambler", []):
        if game_state.round_number < 2:
            continue
        alive_others = [s for s in game_state.alive_seats() if s != action.actor_seat]
        if not alive_others:
            continue
        target = random.choice(alive_others)
        target_faction = get_role_meta(game_state.players[target].role_id).faction
        if target_faction == Faction.WOLF:
            kills[target] = DeathCause.WOLF_BITE.value
        else:
            kills[action.actor_seat] = DeathCause.GAMBLER_MISS.value


def _apply_huntress(game_state, by_role, kills) -> None:
    for action in by_role.get("huntress", []):
        actor = game_state.players[action.actor_seat]
        if actor.role_state.get("used") or action.target_seat is None:
            continue
        kills[action.target_seat] = DeathCause.HUNTRESS.value
        actor.role_state["used"] = True


def _apply_witch(game_state, by_role, kills) -> None:
    for action in by_role.get("witch", []):
        witch = game_state.players[action.actor_seat]
        if action.action_subtype == "heal" and witch.role_state.get("has_heal_potion") and action.target_seat is not None:
            kills.pop(action.target_seat, None)
            witch.role_state["has_heal_potion"] = False
        elif action.action_subtype == "poison" and witch.role_state.get("has_poison_potion") and action.target_seat is not None:
            kills[action.target_seat] = DeathCause.WITCH_POISON.value
            witch.role_state["has_poison_potion"] = False


def _apply_solo_killer(game_state, by_role, kills) -> None:
    for action in by_role.get("solo_killer", []):
        if action.target_seat is not None:
            kills[action.target_seat] = DeathCause.SOLO_KILLER.value


def _apply_vampire(game_state, by_role) -> None:
    for action in by_role.get("vampire", []):
        if action.target_seat is not None:
            game_state.vampire_pending_deaths.append(
                {"seat_id": action.target_seat, "cause": DeathCause.VAMPIRE.value, "announce_round": game_state.round_number + 1}
            )


def _apply_cult_leader(game_state, by_role) -> None:
    for action in by_role.get("cult_leader", []):
        if action.target_seat is not None:
            game_state.cult_members.add(action.target_seat)


def _apply_hunter_mark(game_state, by_role) -> None:
    for action in by_role.get("hunter", []):
        if action.target_seat is not None:
            game_state.players[action.actor_seat].role_state["marked_target"] = action.target_seat


def _gather_info(game_state, by_role, info) -> None:
    from roles import get_role_meta as meta_of
    from roles.villagers import ApprenticeSeer
    from roles.wolves import Medium

    for action in by_role.get("seer", []):
        if action.target_seat is not None:
            info[action.actor_seat] = {"type": "seer", "target_seat": action.target_seat, "faction": meta_of(game_state.players[action.target_seat].role_id).faction.value}

    for action in by_role.get("mystic_seer", []):
        if action.target_seat is not None:
            info[action.actor_seat] = {"type": "mystic_seer", "target_seat": action.target_seat, "role_id": game_state.players[action.target_seat].role_id}

    for action in by_role.get("apprentice_seer", []):
        if ApprenticeSeer.is_active(game_state) and action.target_seat is not None:
            info[action.actor_seat] = {"type": "seer", "target_seat": action.target_seat, "faction": meta_of(game_state.players[action.target_seat].role_id).faction.value}

    for action in by_role.get("wolf_seer", []):
        if action.target_seat is not None:
            info[action.actor_seat] = {"type": "seer", "target_seat": action.target_seat, "faction": meta_of(game_state.players[action.target_seat].role_id).faction.value}

    for action in by_role.get("medium", []):
        if Medium.is_active(game_state) and action.target_seat is not None:
            info[action.actor_seat] = {"type": "seer", "target_seat": action.target_seat, "faction": meta_of(game_state.players[action.target_seat].role_id).faction.value}

    for action in by_role.get("clairvoyant", []):
        if action.target_seat is not None and action.target_seat_2 is not None:
            fa = meta_of(game_state.players[action.target_seat].role_id).faction
            fb = meta_of(game_state.players[action.target_seat_2].role_id).faction
            info[action.actor_seat] = {"type": "clairvoyant", "target_seat": action.target_seat, "target_seat_2": action.target_seat_2, "same_faction": fa == fb}

    for action in by_role.get("detective", []):
        actor = game_state.players[action.actor_seat]
        if actor.role_state.get("used") or action.target_seat is None:
            continue
        is_wolf = meta_of(game_state.players[action.target_seat].role_id).faction == Faction.WOLF
        info[action.actor_seat] = {"type": "detective", "target_seat": action.target_seat, "is_wolf": is_wolf}
        actor.role_state["used"] = True

    for action in by_role.get("sorcerer", []):
        if action.target_seat is not None:
            game_state.players[action.target_seat].role_state["silenced_until_round"] = game_state.round_number + 1

    for action in by_role.get("old_hag", []):
        if action.target_seat is not None:
            target = game_state.players[action.target_seat]
            target.role_state["silenced_until_round"] = game_state.round_number + 1
            target.role_state["vote_banned_until_round"] = game_state.round_number + 1

    if game_state.red_hood_seat is not None:
        grandmother = game_state.players.get(game_state.grandmother_seat) if game_state.grandmother_seat else None
        if grandmother and not grandmother.is_alive:
            wolves = game_state.faction_seats(Faction.WOLF)
            if wolves:
                info[game_state.red_hood_seat] = {"type": "red_hood_hint", "wolf_seat": random.choice(wolves)}


def _apply_converts(game_state, converts) -> None:
    for seat_id, new_role in converts.items():
        game_state.players[seat_id].role_id = new_role


def _resolve_delayed_deaths(game_state, kills) -> None:
    due = [seat for seat, d in game_state.delayed_deaths.items() if d["resolve_round"] <= game_state.round_number]
    for seat in due:
        kills[seat] = game_state.delayed_deaths.pop(seat)["cause"]


def _apply_hunter_counter_kill(game_state, kills) -> None:
    for seat_id in list(kills.keys()):
        player = game_state.players[seat_id]
        if player.role_id == "hunter":
            marked = player.role_state.get("marked_target")
            if marked is not None and marked not in kills and game_state.players[marked].is_alive:
                kills[marked] = DeathCause.HUNTER_MARK.value


def _apply_cupid_chain(game_state, kills) -> None:
    changed = True
    while changed:
        changed = False
        for seat_a, seat_b in game_state.cupid_links:
            for dead_seat, partner in ((seat_a, seat_b), (seat_b, seat_a)):
                still_alive = game_state.players[partner].is_alive and partner not in kills
                if dead_seat in kills and still_alive:
                    kills[partner] = DeathCause.CUPID_LINK.value
                    changed = True


def _apply_terrorist_chain(game_state, kills) -> None:
    order = game_state.seat_order
    if not order:
        return
    changed = True
    while changed:
        changed = False
        for seat_id in list(kills.keys()):
            player = game_state.players[seat_id]
            if player.role_id != "terrorist" or player.role_state.get("chain_applied"):
                continue
            player.role_state["chain_applied"] = True
            idx = order.index(seat_id)
            for neighbour in (order[idx - 1], order[(idx + 1) % len(order)]):
                if game_state.players[neighbour].is_alive and neighbour not in kills:
                    kills[neighbour] = DeathCause.TERRORIST.value
                    changed = True


def _apply_clone_inheritance(game_state, kills) -> None:
    from roles.villagers import Witch

    for player in game_state.players.values():
        if player.role_id != "clone" or not player.is_alive:
            continue
        target_seat = player.role_state.get("clone_target")
        if target_seat is None or player.role_state.get("inherited"):
            continue
        target = game_state.players[target_seat]
        target_died = target_seat in kills or not target.is_alive
        if not target_died:
            continue
        player.role_id = target.role_id
        player.role_state = Witch.init_state() if target.role_id == "witch" else {}
        player.role_state["inherited"] = True


def _apply_drunkard_reroll(game_state) -> None:
    from roles import ROLE_REGISTRY

    if game_state.round_number < 2:
        return
    for player in game_state.players.values():
        if player.role_id != "drunkard" or not player.is_alive:
            continue
        if random.random() < DRUNKARD_SOBER_UP_CHANCE:
            pool = [r for r in ROLE_REGISTRY if r not in ("drunkard", "villager")]
            player.role_id = random.choice(pool)
            player.role_state = {}


def _apply_deaths(game_state, kills) -> list[dict]:
    deaths = []
    for seat_id, cause in kills.items():
        game_state.kill_player(seat_id, cause)
        deaths.append({"seat_id": seat_id, "cause": cause})
    return deaths
