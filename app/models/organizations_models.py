from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, text
from typing import TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.documents_models import Document

class Organization(Base):
    __tablename__ = "organizations"
    """Модель организации для хранения информации об организациях в базе данных."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # ВАЖНО: строковый server_default ("true") попадает в DDL как текстовый литерал
    # DEFAULT 'true', и SQLite хранит строку, которую не находит фильтр is_active == True.
    # Поэтому только text("1") / text("0").
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default=text("1"))

    documents: Mapped[list["Document"]] = relationship("Document", back_populates="organization", cascade="all, delete-orphan")

