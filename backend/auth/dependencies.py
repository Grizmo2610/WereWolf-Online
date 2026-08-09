from dataclasses import dataclass

from fastapi import HTTPException, Request

from auth.service import AuthError, verify_jwt

SESSION_COOKIE_NAME = "session_token"


@dataclass
class CurrentUser:
    user_id: str
    username: str
    display_name: str


async def get_current_user(request: Request) -> CurrentUser:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    try:
        payload = verify_jwt(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return CurrentUser(
        user_id=payload["user_id"],
        username=payload["username"],
        display_name=payload["display_name"],
    )


async def get_current_user_ws(token: str | None) -> CurrentUser | None:
    """Same as get_current_user but for WebSocket handshake, where the cookie
    is read manually and failures should close the socket, not raise HTTP."""
    if not token:
        return None
    try:
        payload = verify_jwt(token)
    except AuthError:
        return None
    return CurrentUser(
        user_id=payload["user_id"],
        username=payload["username"],
        display_name=payload["display_name"],
    )
