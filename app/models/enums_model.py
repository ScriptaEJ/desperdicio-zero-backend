# app/models/enums.py

from enum import Enum


class PerfilUsuario(str, Enum):
    user = "user"


class TipoRegistroPerda(str, Enum):
    insumo = "insumo"
    sobra_prato = "sobra_prato"
    sobra_buffet = "sobra_buffet"


class MotivoPerda(str, Enum):
    vencimento = "vencimento"
    sobra = "sobra"
    erro_preparo = "erro_preparo"
    devolucao = "devolucao"
    quebra = "quebra"


class Turno(str, Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"


class CategoriaInsumos(str, Enum):
    hortifruti = "hortifruti"
    laticinio = "laticinio"
    proteinas = "proteinas"
    mercearia = "mercearia"
    bebidas = "bebidas"


class UnidadeMedida(str, Enum):
    kg = "kg"
    g = "g"
    L = "L"
    ml = "ml"
    unidade = "unidade"