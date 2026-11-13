"""renomear senha_hash para senha

Revision ID: 2f2e4f6c463d
Revises: 28138d71187b
Create Date: 2026-11-13 13:41:39.791526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2f2e4f6c463d'
down_revision: Union[str, Sequence[str], None] = '28138d71187b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "usuarios",
        "senha_hash",
        new_column_name="senha",
        existing_type=sa.String(length=255),
        existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "usuarios",
        "senha",
        new_column_name="senha_hash",
        existing_type=sa.String(length=255),
        existing_nullable=False
    )