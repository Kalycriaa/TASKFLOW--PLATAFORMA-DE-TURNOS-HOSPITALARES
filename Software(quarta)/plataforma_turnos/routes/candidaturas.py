from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Candidatura, Profissional, Turno
from ..services.workflow import aceitar_candidatura, cancelar_candidatura, criar_candidatura, recusar_candidatura


candidaturas_bp = Blueprint("candidaturas", __name__)


@candidaturas_bp.route("/turnos/<int:turno_id>/candidaturas", methods=["POST"])
def candidatar_profissional(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    dados = request.get_json(silent=True) or {}
    profissional_id = dados.get("profissional_id")
    if profissional_id is None:
        return jsonify({"erro": "profissional_id e obrigatorio"}), 400

    profissional = db.session.get(Profissional, int(profissional_id))
    if not profissional:
        return jsonify({"erro": "Profissional nao encontrado"}), 404

    try:
        candidatura, criada = criar_candidatura(turno, profissional)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    status_code = 201 if criada else 200
    mensagem = "Candidatura criada com sucesso" if criada else "Candidatura ja existia"
    return jsonify({"mensagem": mensagem, "candidatura": candidatura.to_dict()}), status_code


@candidaturas_bp.route("/turnos/<int:turno_id>/candidaturas", methods=["GET"])
def listar_candidaturas_turno(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    candidaturas = Candidatura.query.filter_by(turno_id=turno_id).order_by(Candidatura.pontuacao_match.desc()).all()
    return jsonify({"turno": turno.to_dict(), "candidaturas": [candidatura.to_dict() for candidatura in candidaturas]})


@candidaturas_bp.route("/candidaturas/<int:candidatura_id>/aceitar", methods=["POST"])
def aceitar_candidatura_route(candidatura_id: int):
    candidatura = db.session.get(Candidatura, candidatura_id)
    if not candidatura:
        return jsonify({"erro": "Candidatura nao encontrada"}), 404

    try:
        aceitar_candidatura(candidatura)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    return jsonify({"mensagem": "Candidatura aceita com sucesso", "candidatura": candidatura.to_dict()})


@candidaturas_bp.route("/candidaturas/<int:candidatura_id>/recusar", methods=["POST"])
def recusar_candidatura_route(candidatura_id: int):
    candidatura = db.session.get(Candidatura, candidatura_id)
    if not candidatura:
        return jsonify({"erro": "Candidatura nao encontrada"}), 404

    try:
        recusar_candidatura(candidatura)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    return jsonify({"mensagem": "Candidatura recusada com sucesso", "candidatura": candidatura.to_dict()})


@candidaturas_bp.route("/candidaturas/<int:candidatura_id>/cancelar", methods=["POST"])
def cancelar_candidatura_route(candidatura_id: int):
    candidatura = db.session.get(Candidatura, candidatura_id)
    if not candidatura:
        return jsonify({"erro": "Candidatura nao encontrada"}), 404

    try:
        cancelar_candidatura(candidatura)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    return jsonify({"mensagem": "Candidatura cancelada com sucesso", "candidatura": candidatura.to_dict()})
