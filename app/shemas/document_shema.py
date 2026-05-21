from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DocumentCreate(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=255, description="Название организации (3-255 символов)")
    user_name: str = Field(..., min_length=3, max_length=255, description="Имя пользователя (3-255 символов)")
    start_at: datetime = Field(..., description="Дата и время начала работ")
    end_at: datetime = Field(..., description="Дата и время окончания работ")

class Document(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор документа")
    organization_name: str = Field(..., description="Название организации")
    user_name: str = Field(..., description="Имя пользователя")
    created_at: datetime = Field(..., description="Дата и время создания документа")
    start_at: datetime = Field(..., description="Дата и время начала работ")
    end_at: datetime = Field(..., description="Дата и время окончания работ")
    status: bool = Field(..., description="Статус документа (активный/неактивный)")

    model_config = ConfigDict(from_attributes=True)