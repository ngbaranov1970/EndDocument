from datetime import datetime

from sqlalchemy import DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    # organization_name: str = Field(..., description="Название организации")
    # user_name: str = Field(..., description="Имя пользователя")
    # created_at: datetime = Field(..., description="Дата и время создания документа")
    # start_at: datetime = Field(..., description="Дата и время начала работ")
    # end_at: datetime = Field(..., description="Дата и время окончания работ")
    # status: bool = Field(..., description="Статус документа (активный/неактивный)")

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(nullable=False)
    organization_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))


