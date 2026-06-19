from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    """Схема для создания пользователя, содержащая имя пользователя и пароль."""
    username: str = Field(..., min_length=3, max_length=255, description="Имя пользователя (3-255 символов)")
    password: str = Field(..., min_length=6, max_length=255, description="Пароль (6-255 символов)")
    email: str = Field(..., min_length=5, max_length=255, description="Электронная почта (5-255 символов)")

class User(BaseModel):
    """Схема для отображения информации о пользователе, содержащая идентификатор, имя пользователя, электронную почту и статус активности."""
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., description="Имя пользователя")
    email: str | None = Field(None, description="Электронная почта пользователя")
    is_active: bool = Field(..., description="Статус активности пользователя")
    created_at: datetime = Field(..., description="Дата и время создания пользователя")

    model_config = ConfigDict(from_attributes=True)