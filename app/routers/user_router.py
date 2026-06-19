from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.users_model import User as UserModel
from app.schemas.user_schema import UserCreate, User as UserSchema
from app.db.db_depends import get_async_db
from app.service.auth import hash_password


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя. Уникальность username и email гарантируется
    на уровне базы данных (UNIQUE constraint) — при конфликте возвращается 409.
    """

    db_user = UserModel(
        username=user.username,
        hashed_password=hash_password(user.password),
        email=user.email,
        is_active=True,
    )

    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    await db.refresh(db_user)
    return db_user
