
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.insumo_model import Insumo
from app.models.perda_model import Perda


class FiltroPeriodoInvalido(Exception):
    pass


class AgrupamentoInvalido(Exception):
    pass


def obter_periodo(filtro: str):
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))

    hoje = agora.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    if filtro == "esta_semana":
        inicio = hoje - timedelta(days=hoje.weekday())

    elif filtro == "este_mes":
        inicio = hoje.replace(day=1)

    elif filtro == "ultimos_90_dias":
        inicio = hoje - timedelta(days=89)

    else:
        raise FiltroPeriodoInvalido(
            "Filtro de período inválido."
        )

    fim = agora

    duracao = fim - inicio

    inicio_anterior = inicio - duracao
    fim_anterior = inicio

    return inicio, fim, inicio_anterior, fim_anterior


def obter_custo_periodo(
    db: Session,
    restaurante_id: UUID,
    inicio: datetime,
    fim: datetime
):
    custo = (
        db.query(
            func.coalesce(func.sum(Perda.valor_total), 0)
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Perda.data_perda >= inicio,
            Perda.data_perda < fim
        )
        .scalar()
    )

    return custo or Decimal("0")


def obter_indicadores(
    db: Session,
    restaurante_id: UUID,
    filtro: str
):
    inicio, fim, inicio_anterior, fim_anterior = obter_periodo(filtro)

    custo_total = obter_custo_periodo(
        db,
        restaurante_id,
        inicio,
        fim
    )

    custo_anterior = obter_custo_periodo(
        db,
        restaurante_id,
        inicio_anterior,
        fim_anterior
    )

    if custo_anterior > 0:
        variacao = (
            (custo_total - custo_anterior) / custo_anterior
        ) * 100

    else:
        variacao = None

    return {
        "custo_total": custo_total,
        "custo_anterior": custo_anterior,
        "variacao_percentual": (
            round(variacao, 2)
            if variacao is not None
            else None
        )
    }


def obter_origem_desperdicio(
    db: Session,
    restaurante_id: UUID,
    filtro: str,
    agrupamento: str
):
    inicio, fim, _, _ = obter_periodo(filtro)

    colunas = {
        "motivo": Perda.motivo,
        "turno": Perda.turno
    }

    if agrupamento not in colunas:
        raise AgrupamentoInvalido(
            "Agrupamento inválido."
        )

    coluna = colunas[agrupamento]

    custo_total = obter_custo_periodo(
        db,
        restaurante_id,
        inicio,
        fim
    )

    resultados = (
        db.query(
            coluna.label("categoria"),
            func.sum(Perda.valor_total).label("valor_total")
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Perda.data_perda >= inicio,
            Perda.data_perda < fim
        )
        .group_by(coluna)
        .order_by(
            func.sum(Perda.valor_total).desc()
        )
        .all()
    )

    itens = []

    for resultado in resultados:
        nome = resultado.categoria

        if nome is None:
            nome = "Não informado"

        elif hasattr(nome, "value"):
            nome = nome.value

        valor_total = resultado.valor_total

        percentual = (
            round((valor_total / custo_total) * 100, 2)
            if custo_total > 0
            else Decimal("0")
        )

        itens.append({
            "categoria": nome,
            "valor_total": valor_total,
            "percentual": percentual
        })

    return {
        "tipo": agrupamento,
        "custo_total": custo_total,
        "itens": itens
    }


def obter_evolucao(
    db: Session,
    restaurante_id: UUID
):
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))

    hoje = agora.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    inicio_semana = hoje - timedelta(days=hoje.weekday())

    inicio_periodo = inicio_semana - timedelta(weeks=5)

    resultados = (
        db.query(
            func.date_trunc(
                "week",
                Perda.data_perda
            ).label("semana"),
            func.sum(Perda.valor_total).label("valor_total")
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Perda.data_perda >= inicio_periodo,
            Perda.data_perda < agora
        )
        .group_by(
            func.date_trunc("week", Perda.data_perda)
        )
        .order_by(
            func.date_trunc("week", Perda.data_perda)
        )
        .all()
    )

    custos_semanais = {
        resultado.semana.date(): resultado.valor_total
        for resultado in resultados
    }

    semanas = []

    for i in range(6):
        inicio = inicio_periodo + timedelta(weeks=i)
        fim = inicio + timedelta(weeks=1)

        valor_total = custos_semanais.get(
            inicio.date(),
            Decimal("0")
        )

        semanas.append({
            "inicio": inicio.date(),
            "fim": fim.date(),
            "valor_total": valor_total
        })

    return {
        "total_semanas": len(semanas),
        "semanas": semanas
    }

def obter_pontos_atencao(
    db: Session,
    restaurante_id: UUID,
    filtro: str
):
    inicio, fim, inicio_anterior, fim_anterior = obter_periodo(filtro)

    pontos = []

    # 1. Maior perda por vencimento

    vencimento = (
        db.query(
            Insumo.nome.label("insumo"),
            func.sum(Perda.valor_total).label("valor_total")
        )
        .join(
            Insumo,
            Perda.insumo_id == Insumo.id
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Perda.motivo == "vencimento",
            Perda.data_perda >= inicio,
            Perda.data_perda < fim
        )
        .group_by(Insumo.nome)
        .order_by(
            func.sum(Perda.valor_total).desc()
        )
        .first()
    )

    if vencimento:
        pontos.append({
            "tipo": "alerta",
            "titulo": "Perdas por vencimento",
            "descricao": (
                f"{vencimento.insumo} gerou "
                f"R$ {vencimento.valor_total:.2f} "
                "em perdas por vencimento neste período."
            )
        })

    # 2. Turnos com custo acima da média

    resultados_turnos = (
        db.query(
            Perda.turno,
            func.sum(Perda.valor_total).label("valor_total")
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Perda.turno.isnot(None),
            Perda.data_perda >= inicio,
            Perda.data_perda < fim
        )
        .group_by(Perda.turno)
        .all()
    )

    custos_turnos = {
        "manha": Decimal("0"),
        "tarde": Decimal("0"),
        "noite": Decimal("0")
    }

    for resultado in resultados_turnos:
        nome_turno = (
            resultado.turno.value
            if hasattr(resultado.turno, "value")
            else resultado.turno
        )

        custos_turnos[nome_turno] = resultado.valor_total

    media_turnos = (
        sum(custos_turnos.values()) / len(custos_turnos)
    )

    nomes_turnos = {
        "manha": "Manhã",
        "tarde": "Tarde",
        "noite": "Noite"
    }

    for turno, custo in custos_turnos.items():
        if custo > media_turnos and media_turnos > 0:
            percentual = (
                (custo - media_turnos) / media_turnos
            ) * 100

            pontos.append({
                "tipo": "atencao",
                "titulo": f"Desperdício elevado no turno da {nomes_turnos[turno].lower()}",
                "descricao": (
                    f"O turno da {nomes_turnos[turno].lower()} "
                    f"apresentou R$ {custo:.2f} em perdas, "
                    f"{percentual:.2f}% acima da média dos turnos."
                )
            })

    # 3. Melhoria na categoria proteínas

    custo_atual_proteinas = (
        db.query(
            func.coalesce(func.sum(Perda.valor_total), 0)
        )
        .join(
            Insumo,
            Perda.insumo_id == Insumo.id
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Insumo.categoria == "proteinas",
            Perda.data_perda >= inicio,
            Perda.data_perda < fim
        )
        .scalar()
    )

    custo_anterior_proteinas = (
        db.query(
            func.coalesce(func.sum(Perda.valor_total), 0)
        )
        .join(
            Insumo,
            Perda.insumo_id == Insumo.id
        )
        .filter(
            Perda.restaurante_id == restaurante_id,
            Insumo.categoria == "proteinas",
            Perda.data_perda >= inicio_anterior,
            Perda.data_perda < fim_anterior
        )
        .scalar()
    )

    if custo_anterior_proteinas > custo_atual_proteinas:
        reducao = (
            (
                custo_anterior_proteinas
                - custo_atual_proteinas
            )
            / custo_anterior_proteinas
        ) * 100

        pontos.append({
            "tipo": "sucesso",
            "titulo": "Melhora na categoria proteínas",
            "descricao": (
                f"As perdas de proteínas caíram "
                f"{reducao:.2f}% em relação ao período anterior."
            )
        })

    return {
        "total_pontos": len(pontos),
        "pontos": pontos
    }