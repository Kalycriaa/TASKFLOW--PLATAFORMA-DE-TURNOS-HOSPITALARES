from typing import Optional

from sqlalchemy import func

from ..extensions import db
from ..models import Avaliacao, Candidatura, Profissional, UnidadeHospitalar
from ..utils import limitar, normalizar_minusculo
from .scoring import calcular_pontuacao_profissional_para_turno


def criar_candidatura(turno, profissional):
    if turno.status != "aberto":
        raise ValueError("O turno nao esta aberto para candidaturas")

    existente = Candidatura.query.filter_by(turno_id=turno.id, profissional_id=profissional.id).first()
    if existente:
        return existente, False

    pontuacao, distancia_km = calcular_pontuacao_profissional_para_turno(profissional, turno)
    candidatura = Candidatura(
        turno_id=turno.id,
        profissional_id=profissional.id,
        status="pendente",
        pontuacao_match=pontuacao,
        distancia_km=distancia_km,
    )
    db.session.add(candidatura)
    return candidatura, True


def aceitar_candidatura(candidatura):
    if candidatura.status != "pendente":
        raise ValueError("Apenas candidaturas pendentes podem ser aceitas")

    turno = candidatura.turno
    if turno.status != "aberto":
        raise ValueError("O turno nao esta disponivel para aceite")

    candidatura.status = "aceita"
    turno.status = "preenchido"
    turno.profissional_confirmado_id = candidatura.profissional_id

    outras_candidaturas = Candidatura.query.filter(
        Candidatura.turno_id == turno.id,
        Candidatura.id != candidatura.id,
        Candidatura.status == "pendente",
    ).all()
    for item in outras_candidaturas:
        item.status = "recusada"

    return candidatura


def recusar_candidatura(candidatura):
    if candidatura.status != "pendente":
        raise ValueError("Apenas candidaturas pendentes podem ser recusadas")

    candidatura.status = "recusada"
    return candidatura


def cancelar_candidatura(candidatura):
    if candidatura.status not in {"pendente", "aceita"}:
        raise ValueError("Apenas candidaturas pendentes ou aceitas podem ser canceladas")

    turno = candidatura.turno
    candidatura.status = "cancelada"

    if turno.profissional_confirmado_id == candidatura.profissional_id:
        turno.profissional_confirmado_id = None
        turno.status = "aberto"

    return candidatura


def concluir_turno(turno):
    if turno.status != "preenchido" or not turno.profissional_confirmado_id:
        raise ValueError("Somente turnos preenchidos podem ser concluidos")

    turno.status = "finalizado"

    candidatura = Candidatura.query.filter_by(
        turno_id=turno.id,
        profissional_id=turno.profissional_confirmado_id,
        status="aceita",
    ).first()
    if candidatura:
        candidatura.status = "concluida"

    return turno


def registrar_avaliacao(turno, autor_tipo: str, nota: float, comentario: Optional[str]):
    autor_tipo_normalizado = normalizar_minusculo(autor_tipo)
    if autor_tipo_normalizado not in {"unidade", "profissional"}:
        raise ValueError("autor_tipo deve ser 'unidade' ou 'profissional'")

    if turno.status != "finalizado" or not turno.profissional_confirmado_id:
        raise ValueError("O turno precisa estar finalizado antes de receber avaliacao")

    nota_validada = limitar(nota, 0, 5)
    if nota_validada != nota:
        raise ValueError("A nota deve estar entre 0 e 5")

    existente = Avaliacao.query.filter_by(turno_id=turno.id, autor_tipo=autor_tipo_normalizado).first()
    if existente:
        raise ValueError("Esse autor ja avaliou este turno")

    avaliacao = Avaliacao(
        turno_id=turno.id,
        profissional_id=turno.profissional_confirmado_id,
        unidade_id=turno.unidade_id,
        autor_tipo=autor_tipo_normalizado,
        nota=nota,
        comentario=comentario,
    )
    db.session.add(avaliacao)
    db.session.flush()

    if autor_tipo_normalizado == "unidade":
        atualizar_avaliacao_media_profissional(turno.profissional_confirmado_id)
    else:
        atualizar_avaliacao_media_unidade(turno.unidade_id)

    return avaliacao


def atualizar_avaliacao_media_profissional(profissional_id: int):
    media = db.session.query(func.avg(Avaliacao.nota)).filter(
        Avaliacao.profissional_id == profissional_id,
        Avaliacao.autor_tipo == "unidade",
    ).scalar()

    profissional = db.session.get(Profissional, profissional_id)
    if profissional:
        profissional.avaliacao_media = round(float(5.0 if media is None else media), 2)


def atualizar_avaliacao_media_unidade(unidade_id: int):
    media = db.session.query(func.avg(Avaliacao.nota)).filter(
        Avaliacao.unidade_id == unidade_id,
        Avaliacao.autor_tipo == "profissional",
    ).scalar()

    unidade = db.session.get(UnidadeHospitalar, unidade_id)
    if unidade:
        unidade.avaliacao_media = round(float(5.0 if media is None else media), 2)
