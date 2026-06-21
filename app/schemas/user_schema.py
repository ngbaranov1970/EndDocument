from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    """Схема для создания пользователя, содержащая имя пользователя и пароль."""
    username: str = Field(..., min_length=3, max_length=255, description="Имя пользователя (3-255 символов)")
    password: str = Field(..., min_length=6, max_length=255, description="Пароль (6-255 символов)")
    email: EmailStr = Field(..., min_length=5, max_length=255, description="Электронная почта (5-255 символов)")


class UserLogin(BaseModel):
    """Схема для входа пользователя, содержащая имя пользователя и пароль."""
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)


class Token(BaseModel):
    """Схема JWT-токена."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема данных, извлекаемых из JWT-токена."""
    username: str | None = None


class User(BaseModel):
    """Схема для отображения информации о пользователе."""
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., description="Имя пользователя")
    email: EmailStr | None = Field(None, description="Электронная почта пользователя")
    is_active: bool = Field(..., description="Статус активности пользователя")
    is_superuser: bool = Field(..., description="Признак суперпользователя")
    created_at: datetime = Field(..., description="Дата и время создания пользователя")

    model_config = ConfigDict(from_attributes=True)


class UserAdminView(BaseModel):
    """Схема пользователя для панели администратора."""
    id: int
    username: str
    email: EmailStr | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
