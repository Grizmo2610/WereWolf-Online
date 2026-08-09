import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config.settings import settings
from db.d1_client import d1

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
BCRYPT_COST_FACTOR = 12


class AuthError(Exception):
    pass


@dataclass
class RegisterInput:
    username: str
    password: str
    display_name: str = ""


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.match(username):
        raise AuthError("Username phải 3-20 ký tự, chỉ chữ/số/gạch dưới")


def validate_password(password: str) -> None:
    if len(password) < 6:
        raise AuthError("Mật khẩu tối thiểu 6 ký tự")


def resolve_display_name(raw_display_name: str, username: str) -> str:
    display_name = (raw_display_name or "").strip()
    if not display_name:
        return username
    if len(display_name) < 3:
        raise AuthError("Display name tối thiểu 3 ký tự")
    if display_name.isdigit():
        raise AuthError("Display name không được là thuần số")
    return display_name


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(BCRYPT_COST_FACTOR)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


async def username_exists(username: str) -> bool:
    rows = await d1.query("SELECT id FROM users WHERE username = ?", [username])
    return len(rows) > 0


async def register_user(data: RegisterInput) -> dict:
    validate_username(data.username)
    validate_password(data.password)
    display_name = resolve_display_name(data.display_name, data.username)

    if await username_exists(data.username):
        raise AuthError("Username đã tồn tại")

    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)
    created_at = datetime.now(timezone.utc).isoformat()

    await d1.execute(
        "INSERT INTO users (id, username, display_name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        [user_id, data.username, display_name, password_hash, created_at],
    )
    return {"id": user_id, "username": data.username, "display_name": display_name}


async def authenticate_user(username: str, password: str) -> dict:
    rows = await d1.query(
        "SELECT id, username, display_name, password_hash FROM users WHERE username = ?", [username]
    )
    if not rows:
        raise AuthError("Sai tài khoản hoặc mật khẩu")
    user = rows[0]
    if not verify_password(password, user["password_hash"]):
        raise AuthError("Sai tài khoản hoặc mật khẩu")
    return {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}


def create_jwt(user: dict) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expire_days)
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "exp": expire_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthError("Token không hợp lệ hoặc đã hết hạn") from exc
