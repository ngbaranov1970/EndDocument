from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_depends import get_async_db
from app.models.documents_models import Document as DocumentModel
from app.models.organizations_models import Organization as OrganizationModel
from app.schemas.document_sсhema import (
    DocumentCreate,
    Document as DocumentSchema,
    DocumentsByOrganization,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый документ, сохраняющий информацию о начале и окончании работ.
    """
    db_document = DocumentModel(**document.model_dump())
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)  # Для получения id и created_at из базы
    return db_document

@router.get("/", response_model=list[DocumentsByOrganization], status_code=status.HTTP_200_OK)
async def get_all_documents(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает документы, сгруппированные по организациям.
    """

    # Выполняем запрос, который объединяет таблицы организаций и документов, сортируя результаты по идентификаторам организаций и документов
    result = await db.execute(
        select(OrganizationModel, DocumentModel)
        .join(DocumentModel, DocumentModel.organization_id == OrganizationModel.id)
        .order_by(OrganizationModel.id, DocumentModel.id)
    )
    # Получаем все строки результата запроса, каждая из которых содержит объект организации и связанный с ней документ
    rows = result.all()

    grouped_documents: dict[int, DocumentsByOrganization] = {}
    for organization, document in rows:
        if organization.id not in grouped_documents:
            grouped_documents[organization.id] = DocumentsByOrganization(
                organization_id=organization.id,
                organization_name=organization.name,
                documents=[],
            )

        grouped_documents[organization.id].documents.append(
            DocumentSchema.model_validate(document)
        )

    return list(grouped_documents.values())
