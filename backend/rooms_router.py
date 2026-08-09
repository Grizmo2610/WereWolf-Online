from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.dependencies import CurrentUser, get_current_user
from room_manager import SERVER_OVERLOAD_MESSAGE, can_accept_connection, room_manager
from scenarios import SCENARIOS

router = APIRouter(prefix="/rooms", tags=["rooms"])


class CreateRoomBody(BaseModel):
    scenario_id: str = "classic"


class JoinRoomBody(BaseModel):
    room_code: str


@router.get("/scenarios")
async def list_scenarios():
    return [
        {
            "id": s.id,
            "name": s.name,
            "suggested_players": s.suggested_players,
            "min_players": s.min_players,
            "max_players": s.max_players,
        }
        for s in SCENARIOS.values()
    ]


@router.post("")
async def create_room(body: CreateRoomBody, current_user: CurrentUser = Depends(get_current_user)):
    if not can_accept_connection():
        raise HTTPException(status_code=503, detail=SERVER_OVERLOAD_MESSAGE)
    if body.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=400, detail="Kịch bản không tồn tại")
    room = room_manager.create_room(current_user.user_id, current_user.display_name, body.scenario_id)
    return {"room_code": room.room_code, "host_seat_id": room.host_seat_id}


@router.post("/join")
async def join_room(body: JoinRoomBody, current_user: CurrentUser = Depends(get_current_user)):
    if not can_accept_connection():
        raise HTTPException(status_code=503, detail=SERVER_OVERLOAD_MESSAGE)
    room = room_manager.get_room(body.room_code)
    if room is None:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    if room.status != "waiting":
        raise HTTPException(status_code=400, detail="Ván đã bắt đầu")
    seat_id = room.add_player(current_user.user_id, current_user.display_name)
    return {"room_code": room.room_code, "seat_id": seat_id}


@router.get("/{room_code}")
async def get_room(room_code: str, current_user: CurrentUser = Depends(get_current_user)):
    room = room_manager.get_room(room_code)
    if room is None:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    return {
        "room_code": room.room_code,
        "scenario_id": room.scenario.id,
        "host_seat_id": room.host_seat_id,
        "status": room.status,
        "seats": [
            {"seat_id": s.seat_id, "user_id": s.user_id, "display_name": s.display_name, "is_ready": s.is_ready}
            for s in room.seats.values()
        ],
    }
