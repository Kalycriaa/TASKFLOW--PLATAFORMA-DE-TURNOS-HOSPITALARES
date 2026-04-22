from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Candidatura, Profissional, Turno
from ..services.location_provider import resolve_coordinates
from ..services.scoring import calcular_pontuacao_turno_para_profissional, classificar_pontuacao
from ..utils import (
    as_float,
    normalizar_maiusculo,
    normalizar_minusculo,
    normalizar_texto,
    serializar_datetime,
    validar_campos_obrigatorios,
)


profissionais_bp = Blueprint("profissionais", __name__, url_prefix="/profissionais")


@profissionais_bp.route("", methods=["POST"])
def cadastrar_profissional():
    dados = request.get_json(silent=True) or {}
    faltantes = validar_campos_obrigatorios(
        dados,
        ["nome", "categoria", "endereco", "cidade", "estado", "preferencia_turno"],
    )
    if faltantes:
        return jsonify({"erro": "Campos obrigatorios ausentes", "campos": faltantes}), 400

    latitude, longitude = resolve_coordinates(dados)

    avaliacao_media = as_float(dados.get("avaliacao_media"), 5.0)
    taxa_aceitacao = as_float(dados.get("taxa_aceitacao"), 0.5)

    profissional = Profissional(
        nome=normalizar_texto(dados["nome"]),
        categoria=normalizar_minusculo(dados["categoria"]),
        registro_conselho=normalizar_texto(dados.get("registro_conselho")),
        endereco=normalizar_texto(dados["endereco"]),
        cidade=normalizar_maiusculo(dados["cidade"]),
        estado=normalizar_maiusculo(dados["estado"]),
        cep=normalizar_texto(dados.get("cep")),
        preferencia_turno=normalizar_minusculo(dados["preferencia_turno"]),
        avaliacao_media=5.0 if avaliacao_media is None else avaliacao_media,
        taxa_aceitacao=0.5 if taxa_aceitacao is None else taxa_aceitacao,
        latitude=latitude,
        longitude=longitude,
    )

    db.session.add(profissional)
    db.session.commit()

    return jsonify({"mensagem": "Profissional cadastrado com sucesso", "profissional": profissional.to_dict()}), 201


@profissionais_bp.route("", methods=["GET"])
def listar_profissionais():
    profissionais = Profissional.query.order_by(Profissional.id.desc()).all()
    return jsonify([profissional.to_dict() for profissional in profissionais])


@profissionais_bp.route("/<int:profissional_id>", methods=["GET"])
def detalhar_profissional(profissional_id: int):
    profissional = db.session.get(Profissional, profissional_id)
    if not profissional:
        return jsonify({"erro": "Profissional nao encontrado"}), 404
    return jsonify(profissional.to_dict())


@profissionais_bp.route("/<int:profissional_id>/oportunidades", methods=["GET"])
def listar_oportunidades(profissional_id: int):
    profissional = db.session.get(Profissional, profissional_id)
    if not profissional:
        return jsonify({"erro": "Profissional nao encontrado"}), 404

    turnos = Turno.query.filter_by(status="aberto").all()
    resultados = []
    for turno in turnos:
        pontuacao, distancia_km = calcular_pontuacao_turno_para_profissional(profissional, turno)
        resultados.append(
            {
                "turno_id": turno.id,
                "unidade": turno.unidade.to_summary() if turno.unidade else None,
                "categoria": turno.categoria,
                "tipo_turno": turno.tipo_turno,
                "status": turno.status,
                "valor": turno.valor,
                "inicio_em": serializar_datetime(turno.inicio_em),
                "fim_em": serializar_datetime(turno.fim_em),
                "distancia_km": round(distancia_km, 2) if distancia_km is not None else None,
                "pontuacao": round(pontuacao, 4),
                "nivel": classificar_pontuacao(pontuacao),
            }
        )

    resultados.sort(key=lambda item: item["pontuacao"], reverse=True)
    return jsonify({"profissional": profissional.to_dict(), "oportunidades": resultados})


@profissionais_bp.route("/<int:profissional_id>/candidaturas", methods=["GET"])
def listar_candidaturas_do_profissional(profissional_id: int):
    profissional = db.session.get(Profissional, profissional_id)
    if not profissional:
        return jsonify({"erro": "Profissional nao encontrado"}), 404

    candidaturas = Candidatura.query.filter_by(profissional_id=profissional_id).order_by(Candidatura.criada_em.desc()).all()
    return jsonify({"profissional": profissional.to_dict(), "candidaturas": [candidatura.to_dict() for candidatura in candidaturas]})
