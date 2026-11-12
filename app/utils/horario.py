from datetime import datetime
from zoneinfo import ZoneInfo

def horario_br():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))
