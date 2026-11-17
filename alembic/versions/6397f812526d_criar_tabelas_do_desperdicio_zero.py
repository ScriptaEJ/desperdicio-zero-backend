from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "6397f812526d"
down_revision: Union[str, Sequence[str], None] = "0ae4072f4468"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Cria cada tipo ENUM uma única vez no PostgreSQL.
categoria_insumos_enum = postgresql.ENUM(
    "hortifruti",
    "laticinio",
    "proteinas",
    "mercearia",
    "bebidas",
    name="categoria_insumos",
    create_type=False,
)
unidade_medida_enum = postgresql.ENUM( 
    "kg",
    "g",
    "L",
    "ml",
    "unidade",
    name="unidade_medida",
    create_type=False,
)

tipo_registro_enum = postgresql.ENUM(
    "insumo",
    "sobra_prato",
    "sobra_buffet",
    name="tipo_registro_perda",
    create_type=False,
)

motivo_perda_enum = postgresql.ENUM(
    "vencimento",
    "sobra",
    "erro_preparo",
    "devolucao",
    "quebra",
    name="motivo_perda",
    create_type=False,
)

turno_enum = postgresql.ENUM(
    "manha",
    "tarde",
    "noite",
    name="turno",
    create_type=False,
)


def upgrade() -> None:
    """Cria as tabelas do Desperdicio Zero sem remover tabelas existentes."""

    bind = op.get_bind()

    categoria_insumos_enum.create(bind, checkfirst=True)
    unidade_medida_enum.create(bind, checkfirst=True)
    tipo_registro_enum.create(bind, checkfirst=True)
    motivo_perda_enum.create(bind, checkfirst=True)
    turno_enum.create(bind, checkfirst=True)

    op.create_table(
        "restaurantes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("cwid", sa.String(length=100), nullable=True),
        sa.Column(
            "custo_medio_kg",
            sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "insumos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("restaurante_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("categoria", categoria_insumos_enum, nullable=False),
        sa.Column("unidade_medida", unidade_medida_enum, nullable=False),
        sa.Column("custo_unitario", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["restaurante_id"], ["restaurantes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "restaurante_usuarios",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("restaurante_id", sa.UUID(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["restaurante_id"], ["restaurantes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurante_id", "usuario_id"),
    )

    op.create_table(
        "perdas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("restaurante_id", sa.UUID(), nullable=False),
        sa.Column("insumo_id", sa.UUID(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("tipo_registro", tipo_registro_enum, nullable=False),
        sa.Column("quantidade", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unidade_medida", unidade_medida_enum, nullable=False),
        sa.Column("custo_unitario", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("motivo", motivo_perda_enum, nullable=False),
        sa.Column("turno", turno_enum, nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("data_perda", sa.DateTime(timezone=True), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["insumo_id"], ["insumos.id"]),
        sa.ForeignKeyConstraint(["restaurante_id"], ["restaurantes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove somente as tabelas criadas por esta revisao."""

    op.drop_table("perdas")
    op.drop_table("restaurante_usuarios")
    op.drop_table("insumos")
    op.drop_table("restaurantes")

    bind = op.get_bind()
    turno_enum.drop(bind, checkfirst=True)
    motivo_perda_enum.drop(bind, checkfirst=True)
    tipo_registro_enum.drop(bind, checkfirst=True)
    unidade_medida_enum.drop(bind, checkfirst=True)
    categoria_insumos_enum.drop(bind, checkfirst=True)
