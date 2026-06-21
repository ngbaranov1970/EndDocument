from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_depends import get_async_db
from app.models.documents_models import Document as DocumentModel
from app.models.organizations_models import Organization as OrganizationModel
from app.schemas.document_sсhema import Document as DocumentSchema, DocumentsByOrganization
from app.service.auth import get_current_user

router = APIRouter(
    prefix="/documents",
    tags=["documents-archive"],
    dependencies=[Depends(get_current_user)],
)


async def _set_archived_state(
    document_id: int,
    is_archived: bool,
    db: AsyncSession,
):
    db_document = await db.get(DocumentModel, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с id={document_id} не найден",
        )

    db_document.is_archived = is_archived

    await db.commit()
    await db.refresh(db_document)
    return db_document


@router.get("/archived", response_model=list[DocumentsByOrganization], status_code=status.HTTP_200_OK)
async def get_archived_documents(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает архивные документы, сгруппированные по организациям.
    """

    result = await db.execute(
        select(OrganizationModel, DocumentModel)
        .join(DocumentModel, DocumentModel.organization_id == OrganizationModel.id)
        .where(DocumentModel.is_archived.is_(True))
        .order_by(OrganizationModel.id, DocumentModel.id)
    )
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


@router.put("/{document_id}/archive", response_model=DocumentSchema, status_code=status.HTTP_200_OK)
async def archive_document(document_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Переводит документ в архив.
    """
    return await _set_archived_state(document_id, True, db)


@router.put("/{document_id}/restore", response_model=DocumentSchema, status_code=status.HTTP_200_OK)
async def restore_document(document_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает документ из архива.
    """
    return await _set_archived_state(document_id, False, db)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Безвозвратно удаляет документ.
    """
    db_document = await db.get(DocumentModel, document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с id={document_id} не найден",
        )

    await db.delete(db_document)
    await db.commit()

