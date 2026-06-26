from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.users_model import User as UserModel
from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    Token,
    TokenRefresh,
    User as UserSchema,
    UserAdminView,
)
from app.db.db_depends import get_async_db
from app.service.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    save_refresh_token_hash,
    verify_and_invalidate_refresh_token,
    get_current_user,
    get_current_superuser,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя.
    Первый зарегистрированный пользователь автоматически получает статус
    суперпользователя и активируется. Все последующие — неактивны до одобрения.
    """
    # Считаем количество существующих пользователей
    count_result = await db.execute(select(func.count()).select_from(UserModel))
    user_count = count_result.scalar()
    is_first = user_count == 0

    db_user = UserModel(
        username=user.username,
        hashed_password=hash_password(user.password),
        email=user.email,
        is_active=is_first,       # первый пользователь сразу активен
        is_superuser=is_first,    # первый пользователь — суперпользователь
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


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя по username и паролю.
    Возвращает пару токенов: access (короткоживущий) и refresh (долгоживущий).
    Неактивные пользователи не могут войти.
    """
    result = await db.execute(
        select(UserModel).where(UserModel.username == user_login.username)
    )
    db_user = result.scalar_one_or_none()

    if db_user is None or not verify_password(
        user_login.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not activated. Please contact the administrator.",
        )

    # Создаём оба токена
    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    # Сохраняем хеш refresh-токена в БД
    await save_refresh_token_hash(db, db_user.username, refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    body: TokenRefresh,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Обновляет пару токенов по валидному refresh-токену.
    Старый refresh-токен при этом инвалидируется (ротация).
    Клиент должен использовать новый refresh_token из ответа.
    """
    username = await verify_and_invalidate_refresh_token(db, body.refresh_token)

    # Выдаём новую пару
    new_access = create_access_token(data={"sub": username})
    new_refresh = create_refresh_token(data={"sub": username})
    await save_refresh_token_hash(db, username, new_refresh)

    return Token(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserSchema)
async def read_current_user(
    current_user: UserModel = Depends(get_current_user),
):
    """Возвращает информацию о текущем аутентифицированном пользователе."""
    return current_user


# ---------------------------------------------------------------------------
# Административные эндпоинты (только для суперпользователей)
# ---------------------------------------------------------------------------

@router.get("/admin/list", response_model=list[UserAdminView])
async def list_users(
    db: AsyncSession = Depends(get_async_db),
    _: UserModel = Depends(get_current_superuser),
):
    """Возвращает список всех пользователей (только для суперпользователей)."""
    result = await db.execute(select(UserModel).order_by(UserModel.created_at))
    return result.scalars().all()


@router.patch("/admin/{user_id}/activate", response_model=UserAdminView)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: UserModel = Depends(get_current_superuser),
):
    """Активирует пользователя (только для суперпользователей)."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/admin/{user_id}/deactivate", response_model=UserAdminView)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: UserModel = Depends(get_current_superuser),
):
    """Деактивирует пользователя (только для суперпользователей)."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user

