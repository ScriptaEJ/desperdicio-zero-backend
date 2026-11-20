import csv
from datetime import date, timedelta
from io import BytesIO, StringIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from sqlalchemy.orm import Session

# AJUSTE: caminhos dos seus módulos
from app.database.database import get_db
from app.dependencies.restaurante_dependency import get_restaurante_id
from app.models.perda_model import Perda
from app.models.insumo_model import Insumo
from app.services.relatorios_services import (
    MOTIVOS, TIPOS, TURNOS,
    _base, _v, agrupado, brl, build_pdf, data_br, motivo_por_turno,
    num, por_insumo, recomendacoes, totais,
)

relatorios_router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

PDF = "application/pdf"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV = "text/csv; charset=utf-8"


def _validar(inicio: date, fim: date):
    if inicio > fim:
        raise HTTPException(status_code=422, detail="A data inicial deve ser anterior à final")
    if (fim - inicio).days > 366:
        raise HTTPException(status_code=422, detail="O período máximo é de 1 ano")
    return inicio, fim


def periodo_semanal(inicio: Optional[date] = Query(None), fim: Optional[date] = Query(None)):
    fim = fim or date.today()
    return _validar(inicio or fim - timedelta(days=6), fim)


def periodo_mensal(inicio: Optional[date] = Query(None), fim: Optional[date] = Query(None)):
    fim = fim or date.today()
    return _validar(inicio or fim.replace(day=1), fim)


def _arquivo(conteudo: bytes, media_type: str, nome: str) -> Response:
    return Response(
        content=conteudo,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


def _pct(parte: float, total: float) -> str:
    return f"{num(parte / total * 100, 1)}%" if total > 0 else "—"


# ----------------------------- 1. EXECUTIVO SEMANAL (PDF) -----------------------------

@relatorios_router.get("/executivo-semanal")
def relatorio_executivo_semanal(
    periodo: tuple = Depends(periodo_semanal),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db),
):
    inicio, fim = periodo
    dias = (fim - inicio).days + 1
    ant_fim, ant_ini = inicio - timedelta(days=1), inicio - timedelta(days=dias)

    total, qtd = totais(db, restaurante_id, inicio, fim)
    total_ant, _ = totais(db, restaurante_id, ant_ini, ant_fim)
    insumos = por_insumo(db, restaurante_id, inicio, fim)
    motivos = agrupado(db, restaurante_id, inicio, fim, Perda.motivo)
    turnos = agrupado(db, restaurante_id, inicio, fim, Perda.turno)

    variacao = (
        f"{'+' if total >= total_ant else ''}{num((total - total_ant) / total_ant * 100, 1)}%"
        if total_ant > 0 else "—"
    )

    blocos = [
        ("h", "Indicadores do período"),
        ("tabela", [
            ["Indicador", "Valor"],
            ["Custo total das perdas", brl(total)],
            ["Registros de perda", str(qtd)],
            ["Período anterior", brl(total_ant)],
            ["Variação", variacao],
        ]),
        ("h", "Itens críticos (maior custo)"),
        ("tabela", [["Insumo", "Quantidade", "Custo", "% do total"]] + [
            [i["nome"], f"{num(i['quantidade'], 3)} {i['unidade']}", brl(i["valor"]), _pct(i["valor"], total)]
            for i in insumos[:5]
        ]) if insumos else ("p", "Nenhuma perda registrada no período."),
        ("h", "Perdas por motivo"),
        ("tabela", [["Motivo", "Registros", "Custo", "% do total"]] + [
            [MOTIVOS.get(m, m), str(q), brl(v), _pct(v, total)] for m, v, q in motivos
        ]) if motivos else ("p", "Sem dados."),
        ("h", "Perdas por turno"),
        ("tabela", [["Turno", "Registros", "Custo", "% do total"]] + [
            [TURNOS.get(t, t), str(q), brl(v), _pct(v, total)] for t, v, q in turnos
        ]) if turnos else ("p", "Sem dados."),
        ("h", "Três recomendações práticas"),
        ("lista", recomendacoes(insumos, motivos, turnos, total)
            or ["Sem perdas no período: mantenha os controles atuais."]),
    ]

    pdf = build_pdf("Relatório executivo semanal", f"Período: {data_br(inicio)} a {data_br(fim)}", blocos)
    return _arquivo(pdf, PDF, f"relatorio-executivo_{inicio}_{fim}.pdf")


# ----------------------------- 2. RESUMO SEMANAL (PDF) -----------------------------

@relatorios_router.get("/resumo-semanal")
def resumo_semanal(
    periodo: tuple = Depends(periodo_semanal),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db),
):
    inicio, fim = periodo
    total, qtd = totais(db, restaurante_id, inicio, fim)
    insumos = por_insumo(db, restaurante_id, inicio, fim)
    motivos = agrupado(db, restaurante_id, inicio, fim, Perda.motivo)
    turnos = agrupado(db, restaurante_id, inicio, fim, Perda.turno)

    blocos = [
        ("h", "Custos"),
        ("tabela", [["Indicador", "Valor"], ["Custo total", brl(total)], ["Registros", str(qtd)]]),
        ("h", "Itens críticos"),
        ("tabela", [["Insumo", "Custo", "% do total"]] + [
            [i["nome"], brl(i["valor"]), _pct(i["valor"], total)] for i in insumos[:3]
        ]) if insumos else ("p", "Nenhuma perda registrada no período."),
        ("h", "Recomendações"),
        ("lista", recomendacoes(insumos, motivos, turnos, total) or ["Sem perdas no período."]),
    ]

    pdf = build_pdf("Resumo semanal", f"Período: {data_br(inicio)} a {data_br(fim)}", blocos)
    return _arquivo(pdf, PDF, f"resumo-semanal_{inicio}_{fim}.pdf")


# ----------------------------- 3. DESPERDÍCIO POR INSUMO (XLSX) -----------------------------

@relatorios_router.get("/desperdicio-por-insumo")
def desperdicio_por_insumo(
    periodo: tuple = Depends(periodo_mensal),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db),
):
    inicio, fim = periodo
    total, _ = totais(db, restaurante_id, inicio, fim)
    insumos = por_insumo(db, restaurante_id, inicio, fim)

    wb = Workbook()
    ws = wb.active
    ws.title = "Desperdício por insumo"
    ws.append(["#", "Insumo", "Categoria", "Unidade", "Quantidade", "Custo total (R$)", "% do total", "Registros"])

    for pos, i in enumerate(insumos, 1):
        ws.append([pos, i["nome"], i["categoria"], i["unidade"], i["quantidade"],
                   i["valor"], (i["valor"] / total) if total else 0, i["registros"]])

    linha_total = len(insumos) + 2
    ws.cell(linha_total, 2, "TOTAL")
    ws.cell(linha_total, 6, total)
    ws.cell(linha_total, 7, 1 if total else 0)
    ws.cell(linha_total, 8, sum(i["registros"] for i in insumos))

    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="14573F")
        c.alignment = Alignment(horizontal="center")
    for c in ws[linha_total]:
        c.font = Font(bold=True)
    for r in range(2, linha_total + 1):
        ws.cell(r, 5).number_format = "#,##0.000"
        ws.cell(r, 6).number_format = '"R$" #,##0.00'
        ws.cell(r, 7).number_format = "0.0%"
    for col, largura in zip("ABCDEFGH", (5, 30, 16, 10, 14, 18, 12, 11)):
        ws.column_dimensions[col].width = largura
    ws.freeze_panes = "A2"

    buf = BytesIO()
    wb.save(buf)
    return _arquivo(buf.getvalue(), XLSX, f"desperdicio-por-insumo_{inicio}_{fim}.xlsx")


# ----------------------------- 4. ANÁLISE DE TURNOS (PDF) -----------------------------

@relatorios_router.get("/analise-turnos")
def analise_turnos(
    periodo: tuple = Depends(periodo_mensal),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db),
):
    inicio, fim = periodo
    total, _ = totais(db, restaurante_id, inicio, fim)
    turnos = agrupado(db, restaurante_id, inicio, fim, Perda.turno)
    principal = motivo_por_turno(db, restaurante_id, inicio, fim)
    mapa = {t: (v, q) for t, v, q in turnos}

    # sempre mostra manhã, tarde e noite, mesmo sem registros
    ordem = ["manha", "tarde", "noite"] + (["_sem"] if None in mapa else [])
    linhas = [["Turno", "Registros", "Custo", "% do total", "Principal motivo"]]
    for t in ordem:
        chave = None if t == "_sem" else t
        v, q = mapa.get(chave, (0.0, 0))
        motivo = MOTIVOS.get(principal.get(chave), "—")
        linhas.append([TURNOS[chave], str(q), brl(v), _pct(v, total), motivo])

    blocos = [
        ("h", "Comparativo entre manhã, tarde e noite"),
        ("tabela", linhas),
    ]
    com_turno = [t for t in turnos if t[0] is not None]
    if com_turno:
        maior, menor = com_turno[0], com_turno[-1]
        blocos += [
            ("h", "Leitura"),
            ("p", f"O turno da {TURNOS[maior[0]].lower()} concentra a maior perda do período ({brl(maior[1])})."),
        ]
        if len(com_turno) > 1:
            blocos.append(("p", f"O menor custo está no turno da {TURNOS[menor[0]].lower()} ({brl(menor[1])})."))
    if None in mapa:
        blocos.append(("p", f"{mapa[None][1]} registro(s) sem turno informado. Preencher o turno melhora esta análise."))

    pdf = build_pdf("Análise de turnos", f"Período: {data_br(inicio)} a {data_br(fim)}", blocos)
    return _arquivo(pdf, PDF, f"analise-turnos_{inicio}_{fim}.pdf")


# ----------------------------- 5. HISTÓRICO DE PERDAS (CSV) -----------------------------

@relatorios_router.get("/historico-perdas")
def historico_perdas(
    periodo: tuple = Depends(periodo_mensal),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db),
):
    inicio, fim = periodo
    registros = (
        _base(db, restaurante_id, inicio, fim, Perda, Insumo.nome)
        .order_by(Perda.data_perda.desc())
        .all()
    )

    out = StringIO()
    w = csv.writer(out, delimiter=";")  # ponto e vírgula: o Excel pt-BR abre em colunas
    w.writerow(["Data", "Insumo", "Tipo", "Quantidade", "Unidade", "Custo unitário",
                "Valor total", "Motivo", "Turno", "Observação"])
    for p, nome_insumo in registros:
        w.writerow([
            p.data_perda.strftime("%d/%m/%Y %H:%M"),
            nome_insumo,
            TIPOS.get(_v(p.tipo_registro), _v(p.tipo_registro)),
            num(float(p.quantidade), 3),
            _v(p.unidade_medida),
            num(float(p.custo_unitario)),
            num(float(p.valor_total)),
            MOTIVOS.get(_v(p.motivo), _v(p.motivo)),
            TURNOS.get(_v(p.turno), _v(p.turno)),
            p.observacao or "",
        ])

    # utf-8-sig: o BOM faz o Excel reconhecer os acentos
    return _arquivo(out.getvalue().encode("utf-8-sig"), CSV, f"historico-perdas_{inicio}_{fim}.csv")