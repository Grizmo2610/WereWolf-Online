from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from auth.dependencies import SESSION_COOKIE_NAME, CurrentUser, get_current_user
from auth.service import AuthError, RegisterInput, authenticate_user, create_jwt, register_user
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_MAX_AGE_SECONDS = settings.jwt_expire_days * 24 * 60 * 60


class RegisterBody(BaseModel):
    username: str
    password: str
    display_name: str = ""


class LoginBody(BaseModel):
    username: str
    password: str


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.env == "production",
        max_age=COOKIE_MAX_AGE_SECONDS,
    )


@router.post("/register")
async def register(body: RegisterBody, response: Response):
    try:
        user = await register_user(RegisterInput(body.username, body.password, body.display_name))
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_jwt(user)
    _set_session_cookie(response, token)
    return {"user": user}


@router.post("/login")
async def login(body: LoginBody, response: Response):
    try:
        user = await authenticate_user(body.username, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    token = create_jwt(user)
    _set_session_cookie(response, token)
    return {"user": user}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "display_name": current_user.display_name,
    }
