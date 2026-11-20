from datetime import date, datetime, time, timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from sqlalchemy import func
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# AJUSTE: caminhos dos seus models
from app.models.perda_model import Perda
from app.models.insumo_model import Insumo

VERDE = colors.HexColor("#14573f")

MOTIVOS = {
    "vencimento": "Vencimento / Validade",
    "sobra": "Sobra",
    "erro_preparo": "Erro de preparo",
    "devolucao": "Devolução",
    "quebra": "Quebra",
}
TURNOS = {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite", None: "Não informado"}
TIPOS = {"insumo": "Insumo", "sobra_prato": "Sobra de prato", "sobra_buffet": "Sobra do buffet"}

DICAS_MOTIVO = {
    "vencimento": "Adote o PEPS (primeiro que entra, primeiro que sai) e revise o volume dos pedidos de itens perecíveis.",
    "sobra": "Ajuste a produção e as porções à demanda real para reduzir sobras.",
    "erro_preparo": "Padronize receitas e reforce o treinamento da equipe de produção.",
    "devolucao": "Alinhe com fornecedores e com o salão as causas das devoluções.",
    "quebra": "Revise o armazenamento e o manuseio dos itens frágeis.",
}


def _v(x):
    """Valor de um enum (ou o próprio valor, se já for texto)."""
    return getattr(x, "value", x)


def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(v: float, casas: int = 2) -> str:
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def data_br(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# ----------------------------- CONSULTAS -----------------------------

def _base(db: Session, rid: int, inicio: date, fim: date, *cols):
    ini = datetime.combine(inicio, time.min)
    lim = datetime.combine(fim + timedelta(days=1), time.min)
    return (
        db.query(*cols)
        .select_from(Perda)
        .join(Insumo, Insumo.id == Perda.insumo_id)
        .filter(
            Perda.restaurante_id == rid,
            Perda.data_perda >= ini,
            Perda.data_perda < lim,
        )
    )


def totais(db, rid, inicio, fim):
    valor, qtd = _base(
        db, rid, inicio, fim,
        func.coalesce(func.sum(Perda.valor_total), 0),
        func.count(Perda.id),
    ).one()
    return float(valor), int(qtd)


def por_insumo(db, rid, inicio, fim):
    rows = (
        _base(
            db, rid, inicio, fim,
            Insumo.nome, Insumo.categoria, Perda.unidade_medida,
            func.sum(Perda.quantidade), func.sum(Perda.valor_total), func.count(Perda.id),
        )
        .group_by(Insumo.nome, Insumo.categoria, Perda.unidade_medida)
        .order_by(func.sum(Perda.valor_total).desc())
        .all()
    )
    return [
        dict(nome=r[0], categoria=_v(r[1]), unidade=_v(r[2]),
             quantidade=float(r[3]), valor=float(r[4]), registros=int(r[5]))
        for r in rows
    ]


def agrupado(db, rid, inicio, fim, coluna):
    rows = (
        _base(db, rid, inicio, fim, coluna, func.sum(Perda.valor_total), func.count(Perda.id))
        .group_by(coluna)
        .order_by(func.sum(Perda.valor_total).desc())
        .all()
    )
    return [(_v(r[0]), float(r[1]), int(r[2])) for r in rows]


def motivo_por_turno(db, rid, inicio, fim):
    rows = (
        _base(db, rid, inicio, fim, Perda.turno, Perda.motivo, func.sum(Perda.valor_total))
        .group_by(Perda.turno, Perda.motivo)
        .all()
    )
    melhor = {}
    for turno, motivo, valor in rows:
        t, m, v = _v(turno), _v(motivo), float(valor)
        if t not in melhor or v > melhor[t][1]:
            melhor[t] = (m, v)
    return {t: m for t, (m, _) in melhor.items()}


def recomendacoes(insumos, motivos, turnos, total):
    """Gera até 3 recomendações a partir dos números do período."""
    recs = []
    if insumos and total > 0:
        top = insumos[0]
        pct = top["valor"] / total * 100
        recs.append(
            f"{top['nome']} concentra {num(pct, 1)}% do custo de perdas ({brl(top['valor'])}). "
            "Revise compras, porcionamento e armazenamento desse item."
        )
    if motivos:
        recs.append(DICAS_MOTIVO.get(motivos[0][0], "Investigue a causa do principal motivo de perda."))
    turnos_ok = [t for t in turnos if t[0] is not None]
    if turnos_ok:
        recs.append(
            f"O turno da {TURNOS[turnos_ok[0][0]].lower()} registra a maior perda "
            f"({brl(turnos_ok[0][1])}). Reforce o controle e o checklist nesse turno."
        )
    return recs


# ----------------------------- PDF -----------------------------

def build_pdf(titulo: str, subtitulo: str, blocos: list) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, title=titulo,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=base["Title"], textColor=VERDE, alignment=0)
    h2 = ParagraphStyle("h2", parent=base["Heading2"], textColor=VERDE, spaceBefore=14)
    corpo = base["BodyText"]

    story = [Paragraph(escape(titulo), h1), Paragraph(escape(subtitulo), corpo), Spacer(1, 10)]

    for tipo, conteudo in blocos:
        if tipo == "h":
            story.append(Paragraph(escape(conteudo), h2))
        elif tipo == "p":
            story.append(Paragraph(escape(conteudo), corpo))
        elif tipo == "lista":
            for i, item in enumerate(conteudo, 1):
                story.append(Paragraph(f"{i}. {escape(item)}", corpo))
        elif tipo == "tabela":
            t = Table(conteudo, repeatRows=1, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), VERDE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f5f4")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d5ddd8")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
        story.append(Spacer(1, 6))

    doc.build(story)
    return buf.getvalue()