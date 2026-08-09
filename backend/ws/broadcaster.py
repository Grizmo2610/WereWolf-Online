from fastapi import WebSocket


class Broadcaster:
    def __init__(self):
        # room_code -> {seat_id: WebSocket}
        self._connections: dict[str, dict[int, WebSocket]] = {}

    def register(self, room_code: str, seat_id: int, websocket: WebSocket) -> None:
        self._connections.setdefault(room_code, {})[seat_id] = websocket

    def unregister(self, room_code: str, seat_id: int) -> None:
        if room_code in self._connections:
            self._connections[room_code].pop(seat_id, None)

    def is_connected(self, room_code: str, seat_id: int) -> bool:
        return seat_id in self._connections.get(room_code, {})

    async def send_to_seat(self, room_code: str, seat_id: int, event_type: str, payload: dict) -> None:
        socket = self._connections.get(room_code, {}).get(seat_id)
        if socket is None:
            return
        await socket.send_json({"type": event_type, "payload": payload})

    async def broadcast(
        self, room_code: str, event_type: str, payload: dict, exclude_seats: set[int] | None = None
    ) -> None:
        exclude_seats = exclude_seats or set()
        for seat_id, socket in list(self._connections.get(room_code, {}).items()):
            if seat_id in exclude_seats:
                continue
            await socket.send_json({"type": event_type, "payload": payload})

    async def broadcast_to_seats(self, room_code: str, seat_ids: list[int], event_type: str, payload: dict) -> None:
        for seat_id in seat_ids:
            await self.send_to_seat(room_code, seat_id, event_type, payload)


broadcaster = Broadcaster()
