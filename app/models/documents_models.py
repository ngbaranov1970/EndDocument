from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, func, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.organizations_models import Organization

class Document(Base):
    __tablename__ = "documents"
    """Модель документа для хранения информации о начале и окончании работ в базе данных."""

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    start_at: Mapped[date] = mapped_column(Date, nullable=False)
    end_at: Mapped[date] = mapped_column(Date, nullable=False)
    is_archived: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))

    organization: Mapped["Organization"] = relationship("Organization", back_populates="documents")


