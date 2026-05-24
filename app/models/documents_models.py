from datetime import date

from sqlalchemy import Date, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"
    """Модель документа для хранения информации о начале и окончании работ в базе данных."""

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(nullable=False)
    organization_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    start_at: Mapped[date] = mapped_column(Date, nullable=False)
    end_at: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))


