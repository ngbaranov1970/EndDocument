from pydantic import BaseModel, Field, ConfigDict

class OrganizationCreate(BaseModel):
    """Схема для создания организации, содержащая информацию о названии организации."""
    name: str = Field(..., min_length=3, max_length=255, description="Название организации (3-255 символов)")

class Organization(BaseModel):
    """Схема для отображения организации, содержащая информацию о названии организации и статусе активности."""
    id: int = Field(..., description="Уникальный идентификатор организации")
    name: str = Field(..., description="Название организации")
    is_active: bool = Field(..., description="Статус активности организации (активная/неактивная)")

    model_config = ConfigDict(from_attributes=True)