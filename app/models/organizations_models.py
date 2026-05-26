from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.documents_models import Document

class Organization(Base):
    __tablename__ = "organizations"
    """Модель организации для хранения информации об организациях в базе данных."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")

    documents: Mapped[list["Document"]] = relationship("Document", back_populates="organization", cascade="all, delete-orphan")

