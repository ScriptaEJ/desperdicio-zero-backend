"""adicionar deleted_at em usuarios

Revision ID: 0ae4072f4468
Revises: 2f2e4f6c463d
Create Date: 2026-11-13 18:32:05.748698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0ae4072f4468'
down_revision: Union[str, Sequence[str], None] = '2f2e4f6c463d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("usuarios", "deleted_at")
