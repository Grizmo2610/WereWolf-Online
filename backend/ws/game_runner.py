import asyncio

from enums import Phase
from game import GameState, NightAction
from resolver import resolve_night
from roles import get_role, get_role_meta
from room_manager import Room
from vote import resolve_vote, skip_discussion_threshold_met
from ws import events as ev
from ws.broadcaster import broadcaster

PHASE_POLL_INTERVAL_SECONDS = 1

# Roles that only act once the "real" holder of their skill has died —
# gated via a role-specific is_active(game_state) classmethod.
CONDITIONAL_ROLES = {"apprentice_seer", "medium"}


class GameRunner:
    def __init__(self, room: Room):
        self.room = room
        self.game_state: GameState = room.game_state
        self.force_end_discussion = False

    async def run(self) -> None:
        while True:
            self.game_state.round_number += 1
            await self._run_night_phase()
            await self._resolve_and_report_night()
            if await self._check_and_announce_winner():
                return

            await self._announce_due_vampire_deaths()
            if await self._check_and_announce_winner():
                return

            self.force_end_discussion = False
            await self._run_discussion_phase()
            await self._run_vote_phase()
            await self._resolve_and_report_vote()
            if await self._check_and_announce_winner():
                return

    async def _run_night_phase(self) -> None:
        gs = self.game_state
        gs.start_new_phase(Phase.NIGHT)
        await broadcaster.broadcast(
            gs.room_code,
            ev.PHASE_CHANGE,
            {"phase": "night", "round": gs.round_number, "duration_seconds": gs.timing.night_seconds, "started_at": gs.phase_started_at},
        )
        await self._send_night_action_requests()
        # wait the full duration even if everyone already submitted —
        # ending early leaks who has (or hasn't) acted yet
        await asyncio.sleep(gs.timing.night_seconds)

    async def _send_night_action_requests(self) -> None:
        gs = self.game_state
        for seat_id, player in gs.players.items():
            if not player.is_alive:
                continue
            role_meta = get_role_meta(player.role_id)
            if not role_meta.acts_at_night:
                continue
            if role_meta.first_night_only and gs.round_number != 1:
                continue
            if role_meta.max_uses is not None and player.role_state.get("used"):
                continue
            if player.role_id in CONDITIONAL_ROLES:
                role_cls = get_role(player.role_id)
                if not role_cls.is_active(gs):
                    continue

            role_cls = get_role(player.role_id)
            valid_targets = role_cls.valid_targets(gs, seat_id)
            needs_second_target = player.role_id in ("clairvoyant", "cupid")
            await broadcaster.send_to_seat(
                gs.room_code,
                seat_id,
                ev.NIGHT_ACTION_REQUEST,
                {
                    "action_type": player.role_id,
                    "valid_targets": valid_targets,
                    "can_change": True,
                    "needs_second_target": needs_second_target,
                },
            )

    async def _resolve_and_report_night(self) -> None:
        gs = self.game_state
        actions = [
            NightAction(
                actor_seat=seat_id,
                target_seat=data.get("target"),
                action_subtype=data.get("subtype"),
                target_seat_2=data.get("target_2"),
            )
            for seat_id, data in gs.submitted_night_actions.items()
        ]
        deaths, info = resolve_night(gs, actions)
        payload_deaths = [
            {
                "seat_id": d["seat_id"],
                "display_name": gs.players[d["seat_id"]].display_name,
                "cause": d["cause"],
                **({"role": gs.players[d["seat_id"]].role_id} if gs.reveal_on_death else {}),
            }
            for d in deaths
        ]
        await broadcaster.broadcast(
            gs.room_code, ev.PHASE_RESULT, {"deaths": payload_deaths, "no_kill": len(deaths) == 0}
        )
        for seat_id, payload in info.items():
            await broadcaster.send_to_seat(gs.room_code, seat_id, ev.NIGHT_INFO_RESULT, payload)

    async def _announce_due_vampire_deaths(self) -> None:
        gs = self.game_state
        due = [d for d in gs.vampire_pending_deaths if d["announce_round"] <= gs.round_number]
        if not due:
            return
        gs.vampire_pending_deaths = [d for d in gs.vampire_pending_deaths if d not in due]
        deaths = []
        for d in due:
            seat_id = d["seat_id"]
            if not gs.players[seat_id].is_alive:
                continue  # already saved or already dead from something else
            gs.kill_player(seat_id, d["cause"])
            deaths.append(
                {
                    "seat_id": seat_id,
                    "display_name": gs.players[seat_id].display_name,
                    "cause": d["cause"],
                    **({"role": gs.players[seat_id].role_id} if gs.reveal_on_death else {}),
                }
            )
        if deaths:
            await broadcaster.broadcast(gs.room_code, ev.PHASE_RESULT, {"deaths": deaths, "no_kill": False})

    async def _run_discussion_phase(self) -> None:
        gs = self.game_state
        gs.start_new_phase(Phase.DISCUSSION)
        await broadcaster.broadcast(
            gs.room_code,
            ev.PHASE_CHANGE,
            {"phase": "discussion", "round": gs.round_number, "duration_seconds": gs.timing.discussion_seconds, "started_at": gs.phase_started_at},
        )
        elapsed = 0
        early_vote_open = False
        while elapsed < gs.timing.discussion_seconds:
            if self.force_end_discussion:
                break
            if not early_vote_open and elapsed >= gs.timing.early_vote_after_seconds:
                early_vote_open = True
            if early_vote_open and skip_discussion_threshold_met(gs):
                break
            await asyncio.sleep(PHASE_POLL_INTERVAL_SECONDS)
            elapsed += PHASE_POLL_INTERVAL_SECONDS

    async def _run_vote_phase(self) -> None:
        gs = self.game_state
        gs.start_new_phase(Phase.VOTE)
        await broadcaster.broadcast(
            gs.room_code,
            ev.PHASE_CHANGE,
            {"phase": "vote", "round": gs.round_number, "duration_seconds": gs.timing.vote_seconds, "started_at": gs.phase_started_at},
        )
        await asyncio.sleep(gs.timing.vote_seconds)

    async def _resolve_and_report_vote(self) -> None:
        gs = self.game_state
        result = resolve_vote(gs)
        payload_deaths = [
            {
                "seat_id": d["seat_id"],
                "display_name": gs.players[d["seat_id"]].display_name,
                "cause": d["cause"],
                "revealed_only": d.get("revealed_only", False),
                **({"role": gs.players[d["seat_id"]].role_id} if gs.reveal_on_death or d.get("revealed_only") else {}),
            }
            for d in result["deaths"]
        ]
        await broadcaster.broadcast(
            gs.room_code, ev.PHASE_RESULT, {"deaths": payload_deaths, "no_kill": len(payload_deaths) == 0}
        )
        if result["winner_faction"]:
            gs.winner_faction = result["winner_faction"]

    async def _check_and_announce_winner(self) -> bool:
        gs = self.game_state
        winner = gs.winner_faction or gs.check_winner()
        if not winner:
            return False
        gs.winner_faction = winner
        gs.phase = Phase.ENDED
        all_roles = [
            {"seat_id": seat_id, "display_name": p.display_name, "role_id": p.role_id}
            for seat_id, p in gs.players.items()
        ]
        await broadcaster.broadcast(gs.room_code, ev.GAME_END, {"winner_faction": winner, "all_roles": all_roles})
        return True
