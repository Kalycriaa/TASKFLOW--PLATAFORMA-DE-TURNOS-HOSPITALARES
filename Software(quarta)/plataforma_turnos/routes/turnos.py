from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Profissional, Turno, UnidadeHospitalar
from ..services.scoring import calcular_pontuacao_profissional_para_turno, classificar_pontuacao
from ..services.workflow import concluir_turno
from ..utils import (
    as_float,
    normalizar_minusculo,
    normalizar_texto,
    parse_iso_datetime,
    validar_campos_obrigatorios,
)


turnos_bp = Blueprint("turnos", __name__, url_prefix="/turnos")


@turnos_bp.route("", methods=["POST"])
def cadastrar_turno():
    dados = request.get_json(silent=True) or {}
    faltantes = validar_campos_obrigatorios(dados, ["unidade_id", "categoria", "tipo_turno"])
    if faltantes:
        return jsonify({"erro": "Campos obrigatorios ausentes", "campos": faltantes}), 400

    unidade = db.session.get(UnidadeHospitalar, int(dados["unidade_id"]))
    if not unidade:
        return jsonify({"erro": "Unidade hospitalar nao encontrada"}), 404

    inicio_em = parse_iso_datetime(dados.get("inicio_em"))
    fim_em = parse_iso_datetime(dados.get("fim_em"))
    if dados.get("inicio_em") and not inicio_em:
        return jsonify({"erro": "inicio_em deve estar em formato ISO 8601"}), 400
    if dados.get("fim_em") and not fim_em:
        return jsonify({"erro": "fim_em deve estar em formato ISO 8601"}), 400

    turno = Turno(
        unidade_id=unidade.id,
        categoria=normalizar_minusculo(dados["categoria"]),
        tipo_turno=normalizar_minusculo(dados["tipo_turno"]),
        status="aberto",
        valor=as_float(dados.get("valor")),
        observacoes=normalizar_texto(dados.get("observacoes")),
        inicio_em=inicio_em,
        fim_em=fim_em,
    )

    db.session.add(turno)
    db.session.commit()

    return jsonify({"mensagem": "Turno criado com sucesso", "turno": turno.to_dict()}), 201


@turnos_bp.route("", methods=["GET"])
def listar_turnos():
    status = normalizar_minusculo(request.args.get("status"))
    unidade_id = request.args.get("unidade_id")

    query = Turno.query
    if status:
        query = query.filter_by(status=status)
    if unidade_id:
        try:
            query = query.filter_by(unidade_id=int(unidade_id))
        except ValueError:
            return jsonify({"erro": "unidade_id precisa ser numerico"}), 400

    turnos = query.order_by(Turno.id.desc()).all()
    return jsonify([turno.to_dict() for turno in turnos])


@turnos_bp.route("/<int:turno_id>", methods=["GET"])
def detalhar_turno(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404
    return jsonify(turno.to_dict())


@turnos_bp.route("/<int:turno_id>/matches", methods=["GET"])
def recomendar_profissionais(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    profissionais = Profissional.query.all()
    if not profissionais:
        return jsonify({"erro": "Nenhum profissional cadastrado"}), 404

    resultados = []
    for profissional in profissionais:
        pontuacao, distancia_km = calcular_pontuacao_profissional_para_turno(profissional, turno)
        resultados.append(
            {
                "profissional": profissional.to_summary(),
                "distancia_km": round(distancia_km, 2) if distancia_km is not None else None,
                "pontuacao": round(pontuacao, 4),
                "nivel": classificar_pontuacao(pontuacao),
            }
        )

    resultados.sort(key=lambda item: item["pontuacao"], reverse=True)
    return jsonify({"turno": turno.to_dict(), "recomendacoes": resultados})


@turnos_bp.route("/<int:turno_id>/concluir", methods=["POST"])
def finalizar_turno(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    try:
        concluir_turno(turno)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    return jsonify({"mensagem": "Turno concluido com sucesso", "turno": turno.to_dict()})
