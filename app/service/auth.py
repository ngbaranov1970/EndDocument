import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.db_depends import get_async_db
from app.models.users_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    Обрезает пароль до 72 байт (ограничение алгоритма bcrypt).
    """
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8")[:72],
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT-токен с указанными данными и временем истечения.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """
    Декодирует и проверяет JWT-токен.
    Возвращает payload токена или выбрасывает исключение при ошибке.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------

def _hash_token(token: str) -> str:
    """SHA-256 хеш токена для хранения в БД."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(data: dict) -> str:
    """
    Создаёт refresh-токен (JWT с длинным сроком жизни и уникальным jti).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    to_encode.update({
        "exp": expire,
        "jti": uuid.uuid4().hex,           # уникальный идентификатор токена
        "type": "refresh",                  # чтобы нельзя было использовать как access
    })
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def save_refresh_token_hash(
    db: AsyncSession, username: str, refresh_token: str
) -> None:
    """
    Сохраняет SHA-256-хеш refresh-токена в БД для пользователя.
    """
    token_hash = _hash_token(refresh_token)
    await db.execute(
        update(User)
        .where(User.username == username)
        .values(refresh_token_hash=token_hash)
    )
    await db.commit()


async def verify_and_invalidate_refresh_token(
    db: AsyncSession, refresh_token: str
) -> str:
    """
    Проверяет refresh-токен:
    1. JWT-подпись и срок действия
    2. Тип токена == 'refresh'
    3. Хеш токена совпадает с хранящимся в БД

    При успехе **инвалидирует** старый токен (ставит NULL в БД)
    и возвращает username владельца.
    """
    # 1. Проверка JWT
    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # 2. Проверка типа токена
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 3. Сверка хеша с БД
    token_hash = _hash_token(refresh_token)
    result = await db.execute(
        select(User).where(
            User.username == username,
            User.refresh_token_hash == token_hash,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or is invalid",
        )

    # 4. Инвалидируем старый токен (защита от повторного использования)
    await db.execute(
        update(User)
        .where(User.username == username)
        .values(refresh_token_hash=None)
    )
    await db.commit()

    return username


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Извлекает текущего пользователя из JWT-токена.
    Используется как зависимость в защищённых эндпоинтах.
    """
    payload = decode_access_token(token)
    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, что текущий пользователь является суперпользователем.
    Используется как зависимость в административных эндпоинтах.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

