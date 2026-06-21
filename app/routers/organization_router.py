from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_depends import get_async_db
from app.models.organizations_models import Organization as OrganizationModel
from app.schemas.organization_schema import OrganizationCreate, Organization as OrganizationSchema
from app.service.auth import get_current_user

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[OrganizationSchema], status_code=status.HTTP_200_OK)
async def get_organizations(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных организаций.
    """
    result = await db.execute(
        select(OrganizationModel)
        .where(OrganizationModel.is_active == True)
        .order_by(OrganizationModel.name)
    )
    return result.scalars().all()


@router.post("/", response_model=OrganizationSchema, status_code=status.HTTP_201_CREATED)
async def create_organization(organization: OrganizationCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт организацию. Если организация с таким именем уже существует — возвращает её.
    """
    existing = await db.execute(
        select(OrganizationModel).where(OrganizationModel.name == organization.name)
    )
    db_org = existing.scalar_one_or_none()

    if db_org:
        return db_org

    db_org = OrganizationModel(name=organization.name)
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org

