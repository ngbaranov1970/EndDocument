"""add organizations table and fix documents FK

Revision ID: a1b2c3d4e5f6
Revises: 8c4ac976bdff
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8c4ac976bdff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём таблицу organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # 2. Удаляем старый столбец organization_name из documents
    op.drop_column('documents', 'organization_name')

    # 3. Добавляем organization_id как FK на organizations
    op.add_column(
        'documents',
        sa.Column('organization_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_documents_organization_id',
        'documents', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    # Откатываем в обратном порядке
    op.drop_constraint('fk_documents_organization_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'organization_id')

    op.add_column(
        'documents',
        sa.Column('organization_name', sa.String(), nullable=False, server_default=''),
    )

    op.drop_table('organizations')

