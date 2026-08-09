import random
import sys

sys.path.insert(0, "/home/claude/backend")

from game import GameState, NightAction
from player import Player
from resolver import resolve_night
from scenarios import CLASSIC
from vote import resolve_vote


def make_game():
    gs = GameState(room_code="TEST", game_id="g1", scenario=CLASSIC, host_seat_id=1)
    roles = {1: "seer", 2: "werewolf", 3: "witch", 4: "hunter", 5: "werewolf", 6: "guard"}
    for seat_id, role_id in roles.items():
        gs.players[seat_id] = Player(user_id=f"u{seat_id}", seat_id=seat_id, display_name=f"P{seat_id}", role_id=role_id)
    gs.players[3].role_state = {"has_heal_potion": True, "has_poison_potion": True}
    return gs


def test_wolf_bite_not_protected_kills():
    gs = make_game()
    actions = [
        NightAction(actor_seat=2, target_seat=3),  # wolf votes seat3
        NightAction(actor_seat=5, target_seat=3),  # wolf votes seat3
        NightAction(actor_seat=6, target_seat=2),  # guard protects seat2 (not the target)
    ]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths)
    assert deaths == [{"seat_id": 3, "cause": "wolf_bite"}], f"expected seat3 wolf_bite, got {deaths}"
    print("PASS: wolf bite kills unprotected target")


def test_wolf_bite_protected_survives():
    gs = make_game()
    actions = [
        NightAction(actor_seat=2, target_seat=3),
        NightAction(actor_seat=5, target_seat=3),
        NightAction(actor_seat=6, target_seat=3),  # guard protects the actual target this time
    ]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths)
    assert deaths == [], f"expected no deaths, got {deaths}"
    print("PASS: guard protection cancels wolf bite")


def test_witch_poison_bypasses_guard():
    gs = make_game()
    actions = [
        NightAction(actor_seat=6, target_seat=1),  # guard protects seat1
        NightAction(actor_seat=3, target_seat=1, action_subtype="poison"),  # witch poisons seat1 anyway
    ]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths)
    assert deaths == [{"seat_id": 1, "cause": "witch_poison"}], f"expected seat1 witch_poison, got {deaths}"
    print("PASS: witch poison ignores guard protection")


def test_witch_heal_cancels_wolf_bite():
    gs = make_game()
    actions = [
        NightAction(actor_seat=2, target_seat=1),
        NightAction(actor_seat=5, target_seat=1),
        NightAction(actor_seat=3, target_seat=1, action_subtype="heal"),
    ]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths)
    assert deaths == [], f"expected heal to cancel the bite, got {deaths}"
    assert gs.players[3].role_state["has_heal_potion"] is False
    print("PASS: witch heal cancels wolf bite and consumes the potion")


def test_hunter_death_drags_marked_target():
    gs = make_game()
    actions = [
        NightAction(actor_seat=2, target_seat=4),  # wolves kill the hunter
        NightAction(actor_seat=5, target_seat=4),
        NightAction(actor_seat=4, target_seat=1),  # hunter marks seat1 before dying
    ]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths)
    seats_killed = {d["seat_id"] for d in deaths}
    assert seats_killed == {4, 1}, f"expected hunter(4) and marked target(1) to both die, got {deaths}"
    print("PASS: hunter death drags marked target down")


def make_game_custom(roles: dict[int, str]):
    gs = GameState(room_code="TEST", game_id="g1", scenario=CLASSIC, host_seat_id=1)
    for seat_id, role_id in roles.items():
        gs.players[seat_id] = Player(user_id=f"u{seat_id}", seat_id=seat_id, display_name=f"P{seat_id}", role_id=role_id)
    gs.seat_order = sorted(gs.players.keys())
    for seat_id, p in gs.players.items():
        if p.role_id == "witch":
            p.role_state = {"has_heal_potion": True, "has_poison_potion": True}
        if p.role_id == "cult_leader":
            gs.cult_members.add(seat_id)
    return gs


def test_cursed_converts_to_werewolf_instead_of_dying():
    gs = make_game_custom({1: "werewolf", 2: "cursed", 3: "villager", 4: "villager"})
    actions = [NightAction(actor_seat=1, target_seat=2)]
    deaths, info = resolve_night(gs, actions)
    print("deaths:", deaths, "cursed role now:", gs.players[2].role_id)
    assert deaths == [], "cursed should not die"
    assert gs.players[2].role_id == "werewolf", "cursed should convert to werewolf"
    print("PASS: cursed converts instead of dying")


def test_terrorist_chain_kills_seat_neighbours():
    gs = make_game_custom({1: "villager", 2: "terrorist", 3: "villager", 4: "witch"})
    # witch poisons the terrorist directly -> neighbours (seat1, seat3) should die too
    gs.players[4].role_state = {"has_heal_potion": True, "has_poison_potion": True}
    actions = [NightAction(actor_seat=4, target_seat=2, action_subtype="poison")]
    deaths, info = resolve_night(gs, actions)
    seats_killed = {d["seat_id"] for d in deaths}
    print("deaths:", deaths)
    assert seats_killed == {1, 2, 3}, f"expected terrorist + both neighbours to die, got {seats_killed}"
    print("PASS: terrorist death chains into seat neighbours")


def test_cupid_link_kills_partner():
    gs = make_game_custom({1: "werewolf", 2: "villager", 3: "cupid", 4: "villager"})
    gs.round_number = 1
    link_action = NightAction(actor_seat=3, target_seat=2, target_seat_2=4)
    bite_action = NightAction(actor_seat=1, target_seat=2)
    deaths, info = resolve_night(gs, [link_action, bite_action])
    seats_killed = {d["seat_id"] for d in deaths}
    print("deaths:", deaths)
    assert seats_killed == {2, 4}, f"expected both cupid-linked seats to die, got {seats_killed}"
    print("PASS: cupid link drags the partner down")


def test_tough_youth_survives_first_bite_dies_next_night():
    gs = make_game_custom({1: "werewolf", 2: "tough_youth", 3: "villager"})
    gs.round_number = 1
    deaths1, _ = resolve_night(gs, [NightAction(actor_seat=1, target_seat=2)])
    assert deaths1 == [], f"tough youth should survive night1, got {deaths1}"
    assert gs.players[2].is_alive

    gs.round_number = 2
    deaths2, _ = resolve_night(gs, [])  # no new bite needed — delayed death resolves on its own
    print("night1 deaths:", deaths1, "night2 deaths:", deaths2)
    assert deaths2 == [{"seat_id": 2, "cause": "wolf_bite"}], f"expected delayed death on round2, got {deaths2}"
    print("PASS: tough youth delays death by exactly one night")


def test_plague_bearer_skips_next_wolf_vote():
    gs = make_game_custom({1: "werewolf", 2: "plague_bearer", 3: "villager", 4: "villager"})
    gs.round_number = 1
    deaths1, _ = resolve_night(gs, [NightAction(actor_seat=1, target_seat=2)])
    assert deaths1 == [{"seat_id": 2, "cause": "wolf_bite"}]
    assert gs.wolf_infection_active is True

    gs.round_number = 2
    deaths2, _ = resolve_night(gs, [NightAction(actor_seat=1, target_seat=3)])
    print("round2 deaths (should be empty, wolves infected):", deaths2)
    assert deaths2 == [], "wolves should skip their bite the night after eating plague bearer"
    assert gs.wolf_infection_active is False, "infection should clear after being skipped once"
    print("PASS: plague bearer makes wolves miss exactly one night")


def test_clone_inherits_target_role_on_death():
    gs = make_game_custom({1: "werewolf", 2: "clone", 3: "witch"})
    gs.round_number = 1
    gs.players[3].role_state = {"has_heal_potion": True, "has_poison_potion": True}
    clone_action = NightAction(actor_seat=2, target_seat=3)
    bite_action = NightAction(actor_seat=1, target_seat=3)
    deaths, info = resolve_night(gs, [clone_action, bite_action])
    print("deaths:", deaths, "clone role now:", gs.players[2].role_id, "clone state:", gs.players[2].role_state)
    assert deaths == [{"seat_id": 3, "cause": "wolf_bite"}]
    assert gs.players[2].role_id == "witch", f"expected clone to inherit witch, got {gs.players[2].role_id}"
    assert gs.players[2].role_state.get("has_poison_potion") is True
    print("PASS: clone inherits target's role once target dies")


def test_alpha_wolf_converts_target_instead_of_killing():
    gs = make_game_custom({1: "alpha_wolf", 2: "villager", 3: "villager"})
    action = NightAction(actor_seat=1, target_seat=2)
    deaths, info = resolve_night(gs, [action])
    print("deaths:", deaths, "target role now:", gs.players[2].role_id)
    assert deaths == [], "alpha wolf conversion should not kill"
    assert gs.players[2].role_id == "werewolf"
    assert gs.players[1].role_state.get("used") is True
    print("PASS: alpha wolf converts target to werewolf")


def test_detective_reports_wolf_status_once():
    gs = make_game_custom({1: "detective", 2: "werewolf", 3: "villager"})
    deaths, info = resolve_night(gs, [NightAction(actor_seat=1, target_seat=2)])
    print("info:", info)
    assert info[1] == {"type": "detective", "target_seat": 2, "is_wolf": True}
    assert gs.players[1].role_state.get("used") is True
    print("PASS: detective correctly identifies a wolf and is one-time use")


def test_clairvoyant_same_faction_check():
    gs = make_game_custom({1: "clairvoyant", 2: "werewolf", 3: "villager", 4: "werewolf"})
    deaths, info = resolve_night(gs, [NightAction(actor_seat=1, target_seat=2, target_seat_2=4)])
    print("info:", info)
    assert info[1]["same_faction"] is True
    print("PASS: clairvoyant detects same-faction pair")


def test_huntress_one_time_kill():
    gs = make_game_custom({1: "huntress", 2: "villager", 3: "villager"})
    deaths, info = resolve_night(gs, [NightAction(actor_seat=1, target_seat=2)])
    print("deaths:", deaths)
    assert deaths == [{"seat_id": 2, "cause": "huntress"}]
    assert gs.players[1].role_state.get("used") is True
    print("PASS: huntress kills once and is consumed")


def test_gambler_kills_wolf_or_dies_trying():
    random.seed(1)
    gs = make_game_custom({1: "gambler", 2: "werewolf"})
    gs.round_number = 2
    deaths, info = resolve_night(gs, [NightAction(actor_seat=1, target_seat=None)])
    print("deaths (gambler vs sole wolf target):", deaths)
    assert deaths == [{"seat_id": 2, "cause": "wolf_bite"}]
    print("PASS: gambler correctly guesses the only remaining wolf")


def test_saboteur_swaps_two_roles():
    random.seed(2)
    gs = make_game_custom({1: "saboteur", 2: "villager", 3: "seer", 4: "villager"})
    resolve_night(gs, [NightAction(actor_seat=1, target_seat=2)])
    roles_after = {seat: p.role_id for seat, p in gs.players.items()}
    print("roles after swap:", roles_after)
    assert roles_after[2] != "villager", "seat2's role should have been swapped away"
    assert gs.players[1].role_state.get("used") is True
    print("PASS: saboteur swaps two players' roles once")


def test_twins_win_as_last_two_survivors():
    gs = make_game_custom({1: "twin", 2: "twin"})
    gs.twin_pairs = [(1, 2)]
    winner = gs.check_winner()
    print("winner:", winner)
    assert winner == "twins"
    print("PASS: twins win when they're the last two standing")


def test_lone_wolf_wins_as_sole_surviving_wolf():
    gs = make_game_custom({1: "lone_wolf", 2: "villager", 3: "villager"})
    winner = gs.check_winner()
    print("winner (lone wolf is the only wolf, even with 2 villagers alive):", winner)
    assert winner == "lone_wolf", f"lone wolf should win as soon as it's the only wolf left, got {winner}"
    print("PASS: lone wolf wins once it's the only wolf remaining")


def test_solo_killer_wins_as_sole_survivor():
    gs = make_game_custom({1: "solo_killer", 2: "villager"})
    gs.players[2].is_alive = False
    winner = gs.check_winner()
    print("winner:", winner)
    assert winner == "solo_killer"
    print("PASS: solo killer wins as the last one standing")


def test_prince_immunity_reveals_instead_of_killing():
    gs = make_game_custom({1: "prince", 2: "villager", 3: "villager"})
    gs.submitted_votes = {2: 1, 3: 1}
    result = resolve_vote(gs)
    print("result:", result)
    assert result["deaths"] == [{"seat_id": 1, "cause": "prince_immunity", "revealed_only": True}]
    assert gs.players[1].is_alive, "prince should survive the first lynch"
    print("PASS: prince survives first lynch via immunity")


def test_fool_wins_when_lynched():
    gs = make_game_custom({1: "fool", 2: "villager", 3: "villager"})
    gs.submitted_votes = {2: 1, 3: 1}
    result = resolve_vote(gs)
    print("result:", result)
    assert result["winner_faction"] == "fool"
    assert not gs.players[1].is_alive
    print("PASS: fool wins by getting lynched")


def test_wolf_cub_death_grants_double_lynch_next_day():
    gs = make_game_custom({1: "wolf_cub", 2: "villager", 3: "villager", 4: "villager"})
    gs.submitted_votes = {2: 1, 3: 1, 4: 1}  # everyone votes wolf_cub (seat1)
    result = resolve_vote(gs)
    print("round1 result:", result, "pending_effects:", gs.pending_effects)
    assert result["deaths"] == [{"seat_id": 1, "cause": "lynch"}]
    assert gs.pending_effects.get("double_lynch_count") == 2
    print("PASS: wolf cub death sets up a double lynch for the next day")


def test_cult_leader_wins_when_all_alive_are_cult():
    gs = make_game_custom({1: "cult_leader", 2: "villager"})
    gs.cult_members = {1, 2}
    winner = gs.check_winner()
    print("winner:", winner)
    assert winner == "cult", f"expected cult win, got {winner}"
    print("PASS: cult leader wins once everyone alive is recruited")


if __name__ == "__main__":
    test_wolf_bite_not_protected_kills()
    test_wolf_bite_protected_survives()
    test_witch_poison_bypasses_guard()
    test_witch_heal_cancels_wolf_bite()
    test_hunter_death_drags_marked_target()
    test_cursed_converts_to_werewolf_instead_of_dying()
    test_terrorist_chain_kills_seat_neighbours()
    test_cupid_link_kills_partner()
    test_tough_youth_survives_first_bite_dies_next_night()
    test_plague_bearer_skips_next_wolf_vote()
    test_cult_leader_wins_when_all_alive_are_cult()
    test_clone_inherits_target_role_on_death()
    test_alpha_wolf_converts_target_instead_of_killing()
    test_detective_reports_wolf_status_once()
    test_clairvoyant_same_faction_check()
    test_huntress_one_time_kill()
    test_gambler_kills_wolf_or_dies_trying()
    test_saboteur_swaps_two_roles()
    test_twins_win_as_last_two_survivors()
    test_lone_wolf_wins_as_sole_surviving_wolf()
    test_solo_killer_wins_as_sole_survivor()
    test_prince_immunity_reveals_instead_of_killing()
    test_fool_wins_when_lynched()
    test_wolf_cub_death_grants_double_lynch_next_day()
    print("\nALL RESOLVER TESTS PASSED")
