from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Avaliacao, Turno
from ..services.workflow import registrar_avaliacao


avaliacoes_bp = Blueprint("avaliacoes", __name__)


@avaliacoes_bp.route("/turnos/<int:turno_id>/avaliacoes", methods=["POST"])
def criar_avaliacao(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    dados = request.get_json(silent=True) or {}
    autor_tipo = dados.get("autor_tipo")
    nota = dados.get("nota")
    comentario = dados.get("comentario")

    if autor_tipo is None or nota is None:
        return jsonify({"erro": "autor_tipo e nota sao obrigatorios"}), 400

    try:
        avaliacao = registrar_avaliacao(turno, autor_tipo=autor_tipo, nota=float(nota), comentario=comentario)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 400

    return jsonify({"mensagem": "Avaliacao registrada com sucesso", "avaliacao": avaliacao.to_dict()}), 201


@avaliacoes_bp.route("/turnos/<int:turno_id>/avaliacoes", methods=["GET"])
def listar_avaliacoes(turno_id: int):
    turno = db.session.get(Turno, turno_id)
    if not turno:
        return jsonify({"erro": "Turno nao encontrado"}), 404

    avaliacoes = Avaliacao.query.filter_by(turno_id=turno_id).order_by(Avaliacao.criado_em.desc()).all()
    return jsonify({"turno": turno.to_dict(), "avaliacoes": [avaliacao.to_dict() for avaliacao in avaliacoes]})
