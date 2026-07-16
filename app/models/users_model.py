from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, text

from app.db.database import Base



class User(Base):
    __tablename__ = "users"
    """Модель пользователя для хранения информации о пользователях в базе данных."""

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # server_default только как text("0")/text("1"): строка "false" стала бы
    # текстовым литералом DEFAULT 'false' в SQLite (см. organizations_models.py)
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default=text("0"))
    is_superuser: Mapped[bool] = mapped_column(nullable=False, server_default=text("0"))

    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    refresh_token_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )