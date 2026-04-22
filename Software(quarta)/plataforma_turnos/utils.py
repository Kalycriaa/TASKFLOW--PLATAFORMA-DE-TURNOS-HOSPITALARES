from datetime import datetime
from typing import Any, Optional


def normalizar_texto(valor: Optional[str]) -> str:
    return (valor or "").strip()


def normalizar_maiusculo(valor: Optional[str]) -> str:
    return normalizar_texto(valor).upper()


def normalizar_minusculo(valor: Optional[str]) -> str:
    return normalizar_texto(valor).lower()


def limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(valor, maximo))


def validar_campos_obrigatorios(dados: dict[str, Any], campos: list[str]) -> list[str]:
    faltantes = []
    for campo in campos:
        valor = dados.get(campo)
        if valor is None:
            faltantes.append(campo)
            continue
        if isinstance(valor, str) and not valor.strip():
            faltantes.append(campo)
    return faltantes


def parse_iso_datetime(valor: Any) -> Optional[datetime]:
    if valor is None:
        return None

    texto = normalizar_texto(str(valor))
    if not texto:
        return None

    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None


def serializar_datetime(valor: Optional[datetime]) -> Optional[str]:
    return valor.isoformat() if valor else None


def as_float(valor: Any, default: Optional[float] = None) -> Optional[float]:
    if valor is None or valor == "":
        return default

    try:
        return float(valor)
    except (TypeError, ValueError):
        return default
