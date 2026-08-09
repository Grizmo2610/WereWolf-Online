import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from auth.dependencies import get_current_user_ws
from enums import AFK_TIMEOUT_SECONDS, Phase
from roles import get_role, get_role_meta
from room_manager import room_manager
from ws import events as ev
from ws.broadcaster import broadcaster
from ws.game_runner import GameRunner

router = APIRouter()

_afk_tasks: dict[tuple[str, int], asyncio.Task] = {}


@router.websocket("/ws/{room_code}")
async def game_socket(websocket: WebSocket, room_code: str):
    token = websocket.cookies.get("session_token") or websocket.query_params.get("token")
    user = await get_current_user_ws(token)
    if user is None:
        await websocket.close(code=4401)
        return

    room = room_manager.get_room(room_code)
    if room is None:
        await websocket.close(code=4404)
        return

    seat_id = _find_seat_for_user(room, user.user_id)
    if seat_id is None:
        await websocket.close(code=4403)
        return

    await websocket.accept()
    broadcaster.register(room_code, seat_id, websocket)
    _cancel_afk_timer(room_code, seat_id)
    await broadcaster.broadcast(room_code, ev.PLAYER_RECONNECTED, {"seat_id": seat_id})
    await _broadcast_room_update(room)
    if room.status == "waiting":
        await broadcaster.send_to_seat(room_code, seat_id, ev.ROOM_SETTINGS_UPDATE, room.settings_payload())

    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            await _dispatch(room, seat_id, msg_type, message.get("payload") or {})
            if msg_type == ev.LEAVE_ROOM:
                await websocket.close()
                return
    except WebSocketDisconnect:
        broadcaster.unregister(room_code, seat_id)
        await broadcaster.broadcast(room_code, ev.PLAYER_DISCONNECTED, {"seat_id": seat_id, "afk_countdown_seconds": AFK_TIMEOUT_SECONDS})
        _start_afk_timer(room, seat_id)


def _find_seat_for_user(room, user_id: str) -> int | None:
    for seat_id, seat in room.seats.items():
        if seat.user_id == user_id:
            return seat_id
    return None


async def _broadcast_room_update(room) -> None:
    players = [
        {"seat_id": seat.seat_id, "user_id": seat.user_id, "display_name": seat.display_name, "is_ready": seat.is_ready}
        for seat in room.seats.values()
    ]
    await broadcaster.broadcast(room.room_code, ev.ROOM_UPDATE, {"players": players, "host_seat_id": room.host_seat_id})


def _start_afk_timer(room, seat_id: int) -> None:
    async def _mark_afk_after_timeout():
        await asyncio.sleep(AFK_TIMEOUT_SECONDS)
        if not broadcaster.is_connected(room.room_code, seat_id):
            if room.game_state and seat_id in room.game_state.players:
                room.game_state.players[seat_id].is_afk = True
            if seat_id == room.host_seat_id:
                await _transfer_host(room)

    _afk_tasks[(room.room_code, seat_id)] = asyncio.create_task(_mark_afk_after_timeout())


def _cancel_afk_timer(room_code: str, seat_id: int) -> None:
    task = _afk_tasks.pop((room_code, seat_id), None)
    if task:
        task.cancel()


async def _transfer_host(room) -> None:
    connected_seats = [s for s in room.seats if broadcaster.is_connected(room.room_code, s)]
    if not connected_seats:
        return
    room.host_seat_id = min(connected_seats)
    await broadcaster.broadcast(room.room_code, ev.HOST_TRANSFERRED, {"new_host_seat_id": room.host_seat_id})


async def _dispatch(room, seat_id: int, event_type: str | None, payload: dict) -> None:
    handler = _HANDLERS.get(event_type)
    if handler is None:
        return
    await handler(room, seat_id, payload)


async def _handle_ready(room, seat_id: int, payload: dict) -> None:
    room.seats[seat_id].is_ready = True
    await _broadcast_room_update(room)


async def _handle_unready(room, seat_id: int, payload: dict) -> None:
    room.seats[seat_id].is_ready = False
    await _broadcast_room_update(room)


async def _handle_leave_room(room, seat_id: int, payload: dict) -> None:
    if room.status != "waiting":
        return  # leaving mid-game isn't supported yet — use disconnect/AFK flow instead
    was_host = seat_id == room.host_seat_id
    room.remove_player(seat_id)
    _cancel_afk_timer(room.room_code, seat_id)
    broadcaster.unregister(room.room_code, seat_id)

    if not room.seats:
        room_manager.delete_room(room.room_code)
        return

    if was_host:
        await broadcaster.broadcast(room.room_code, ev.HOST_TRANSFERRED, {"new_host_seat_id": room.host_seat_id})
    await _broadcast_room_update(room)


async def _handle_update_room_settings(room, seat_id: int, payload: dict) -> None:
    if seat_id != room.host_seat_id or room.status != "waiting":
        return
    room.update_settings(payload)
    await broadcaster.broadcast(room.room_code, ev.ROOM_SETTINGS_UPDATE, room.settings_payload())


async def _handle_start_game(room, seat_id: int, payload: dict) -> None:
    if seat_id != room.host_seat_id or not room.can_start():
        return
    from ws.game_start import start_game

    await start_game(room)
    room.runner = GameRunner(room)
    asyncio.create_task(room.runner.run())


async def _handle_night_action(room, seat_id: int, payload: dict, subtype: str | None = None) -> None:
    gs = room.game_state
    if gs is None or gs.phase != Phase.NIGHT:
        return
    player = gs.players.get(seat_id)
    if player is None or not player.is_alive:
        return
    role_meta = get_role_meta(player.role_id)
    if not role_meta.acts_at_night:
        return
    target = payload.get("target_seat")
    target_2 = payload.get("target_seat_2")
    role_cls = get_role(player.role_id)
    valid = role_cls.valid_targets(gs, seat_id)
    if target is not None and target not in valid:
        return
    if target_2 is not None and (target_2 not in valid or target_2 == target):
        return
    gs.submitted_night_actions[seat_id] = {
        "target": target,
        "target_2": target_2,
        "subtype": subtype or payload.get("action_subtype"),
    }


async def _handle_wolf_vote(room, seat_id: int, payload: dict) -> None:
    await _handle_night_action(room, seat_id, payload)


async def _handle_day_speak(room, seat_id: int, payload: dict) -> None:
    gs = room.game_state
    if gs is None:
        return
    player = gs.players.get(seat_id)
    if player is None:
        return
    text = (payload.get("text") or "").strip()
    if not text:
        return
    channel = payload.get("channel", "public")

    if channel == "public":
        if not player.is_alive and not player.role_state.get("is_ghost"):
            return
        if gs.phase != Phase.DISCUSSION:
            return
        if player.role_state.get("is_ghost"):
            if player.role_state.get("ghost_spoke_round") == gs.round_number:
                return
            if len(text.split()) > 1:
                return
            player.role_state["ghost_spoke_round"] = gs.round_number
        if player.role_state.get("silenced_until_round") == gs.round_number:
            return
        await broadcaster.broadcast(
            gs.room_code, ev.PLAYER_SPEAK, {"seat_id": seat_id, "display_name": player.display_name, "text": text, "channel": "public"}
        )
    elif channel == "dead":
        if player.is_alive:
            return
        dead_seats = [s for s, p in gs.players.items() if not p.is_alive]
        await broadcaster.broadcast_to_seats(
            gs.room_code, dead_seats, ev.DEAD_CHAT, {"seat_id": seat_id, "display_name": player.display_name, "text": text, "channel": "dead"}
        )


async def _handle_skip_discussion(room, seat_id: int, payload: dict) -> None:
    gs = room.game_state
    if gs is None or gs.phase != Phase.DISCUSSION:
        return
    if seat_id not in gs.alive_seats():
        return
    gs.skip_votes.add(seat_id)
    if seat_id == room.host_seat_id and room.runner is not None:
        room.runner.force_end_discussion = True  # host can end discussion any time, no ratio needed

    await broadcaster.broadcast(
        gs.room_code,
        ev.SKIP_VOTE_UPDATE,
        {"skip_count": len(gs.skip_votes), "required": max(1, len(gs.alive_seats()) // 2 + 1)},
    )


async def _handle_vote(room, seat_id: int, payload: dict) -> None:
    gs = room.game_state
    if gs is None or gs.phase != Phase.VOTE:
        return
    if seat_id not in gs.alive_seats():
        return
    player = gs.players[seat_id]
    if player.role_state.get("vote_banned_until_round") == gs.round_number:
        return
    target = payload.get("target_seat")
    gs.submitted_votes[seat_id] = target
    counts = {}
    for t in gs.submitted_votes.values():
        if t is not None:
            counts[t] = counts.get(t, 0) + 1
    await broadcaster.broadcast(
        gs.room_code,
        ev.VOTE_UPDATE,
        {"counts": counts, "total_voted": len(gs.submitted_votes), "total_eligible": len(gs.alive_seats())},
    )


_HANDLERS = {
    ev.READY: _handle_ready,
    ev.UNREADY: _handle_unready,
    ev.LEAVE_ROOM: _handle_leave_room,
    ev.UPDATE_ROOM_SETTINGS: _handle_update_room_settings,
    ev.START_GAME: _handle_start_game,
    ev.NIGHT_ACTION: _handle_night_action,
    ev.CHANGE_NIGHT_ACTION: _handle_night_action,
    ev.WOLF_VOTE: _handle_wolf_vote,
    ev.CHANGE_WOLF_VOTE: _handle_wolf_vote,
    ev.DAY_SPEAK: _handle_day_speak,
    ev.SKIP_DISCUSSION: _handle_skip_discussion,
    ev.VOTE: _handle_vote,
    ev.CHANGE_VOTE: _handle_vote,
}
