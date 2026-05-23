from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_depends import get_async_db
from app.models.documents_models import Document as DocumentModel
from app.schemas.document_sсhema import DocumentCreate, Document as DocumentSchema

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

@router.get("/", response_model=DocumentSchema, status_code=status.HTTP_200_OK)
async def get_all_documents(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех документов.
    """
    result = await db.execute(select(DocumentModel))
    documents = result.scalars().all()
    return documents