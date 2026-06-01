"""set organization_id not null in documents

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-01 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем старые записи без organization_id (остались от прежней схемы)
    op.execute("DELETE FROM documents WHERE organization_id IS NULL")

    # Теперь безопасно устанавливаем NOT NULL
    op.alter_column(
        'documents',
        'organization_id',
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'documents',
        'organization_id',
        existing_type=sa.Integer(),
        nullable=True,
    )

