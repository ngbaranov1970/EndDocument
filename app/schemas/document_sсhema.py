from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class DocumentCreate(BaseModel):
    """Схема для создания документа, содержащая информацию о названии организации, имени пользователя, дате и времени начала и окончания работ."""
    organization_name: str = Field(..., min_length=3, max_length=255, description="Название организации (3-255 символов)")
    user_name: str = Field(..., min_length=3, max_length=255, description="Имя пользователя (3-255 символов)")
    start_at: date = Field(..., description="Дата и время начала работ")
    end_at: date = Field(..., description="Дата и время окончания работ")

class Document(BaseModel):
    """Схема для отображения документа, содержащая информацию о названии организации, имени пользователя, дате и времени начала и окончания работ, а также статус документа."""
    id: int = Field(..., description="Уникальный идентификатор документа")
    organization_id: int = Field(..., description="Идентификатор организации")
    user_name: str = Field(..., description="Имя пользователя")
    created_at: date = Field(..., description="Дата и время создания документа")
    start_at: date = Field(..., description="Дата и время начала работ")
    end_at: date = Field(..., description="Дата и время окончания работ")
    status: bool = Field(..., description="Статус документа (активный/неактивный)")

    model_config = ConfigDict(from_attributes=True)


class DocumentsByOrganization(BaseModel):
    """Схема ответа для группировки документов по организациям."""
    organization_id: int = Field(..., description="Идентификатор организации")
    organization_name: str = Field(..., description="Название организации")
    documents: list[Document] = Field(default_factory=list, description="Документы организации")
