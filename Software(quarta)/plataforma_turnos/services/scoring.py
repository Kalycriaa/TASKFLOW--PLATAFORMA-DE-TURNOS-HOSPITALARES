from typing import Optional, Tuple

from ..utils import limitar, normalizar_minusculo
from .location_provider import calculate_distance_km


def calcular_pontuacao_profissional_para_turno(profissional, turno) -> Tuple[float, Optional[float]]:
    unidade = turno.unidade
    distancia_km = calculate_distance_km(
        profissional.latitude,
        profissional.longitude,
        unidade.latitude if unidade else None,
        unidade.longitude if unidade else None,
    )

    nota_avaliacao = limitar((profissional.avaliacao_media or 0) / 5, 0, 1)
    nota_aceitacao = limitar(profissional.taxa_aceitacao or 0, 0, 1)
    nota_turno = 1.0 if normalizar_minusculo(profissional.preferencia_turno) == normalizar_minusculo(turno.tipo_turno) else 0.0
    nota_categoria = 1.0 if normalizar_minusculo(profissional.categoria) == normalizar_minusculo(turno.categoria) else 0.0

    if distancia_km is None:
        nota_distancia = 0.4
    else:
        nota_distancia = 1 / (1 + (distancia_km / 10))

    pontuacao = (
        nota_avaliacao * 0.45
        + nota_distancia * 0.25
        + nota_aceitacao * 0.15
        + nota_turno * 0.10
        + nota_categoria * 0.05
    )
    return pontuacao, distancia_km


def calcular_pontuacao_turno_para_profissional(profissional, turno) -> Tuple[float, Optional[float]]:
    pontuacao_base, distancia_km = calcular_pontuacao_profissional_para_turno(profissional, turno)

    bonus_unidade = 0.0
    if turno.unidade and turno.unidade.avaliacao_media is not None:
        bonus_unidade = limitar(turno.unidade.avaliacao_media / 5, 0, 1) * 0.10

    pontuacao_final = limitar(pontuacao_base * 0.90 + bonus_unidade, 0, 1)
    return pontuacao_final, distancia_km


def classificar_pontuacao(pontuacao: float) -> str:
    if pontuacao >= 0.80:
        return "Alta aderencia"
    if pontuacao >= 0.55:
        return "Media aderencia"
    return "Baixa aderencia"
