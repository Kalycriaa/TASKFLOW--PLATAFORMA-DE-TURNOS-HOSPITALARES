from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Turno, UnidadeHospitalar
from ..services.location_provider import resolve_coordinates
from ..utils import as_float, normalizar_maiusculo, normalizar_texto, validar_campos_obrigatorios


unidades_bp = Blueprint("unidades", __name__, url_prefix="/unidades")


@unidades_bp.route("", methods=["POST"])
def cadastrar_unidade():
    dados = request.get_json(silent=True) or {}
    faltantes = validar_campos_obrigatorios(dados, ["nome", "endereco", "cidade", "estado"])
    if faltantes:
        return jsonify({"erro": "Campos obrigatorios ausentes", "campos": faltantes}), 400

    latitude, longitude = resolve_coordinates(dados)

    avaliacao_media = as_float(dados.get("avaliacao_media"), 5.0)

    unidade = UnidadeHospitalar(
        nome=normalizar_texto(dados["nome"]),
        endereco=normalizar_texto(dados["endereco"]),
        cidade=normalizar_maiusculo(dados["cidade"]),
        estado=normalizar_maiusculo(dados["estado"]),
        cep=normalizar_texto(dados.get("cep")),
        avaliacao_media=5.0 if avaliacao_media is None else avaliacao_media,
        latitude=latitude,
        longitude=longitude,
    )

    db.session.add(unidade)
    db.session.commit()

    return jsonify({"mensagem": "Unidade cadastrada com sucesso", "unidade": unidade.to_dict()}), 201


@unidades_bp.route("", methods=["GET"])
def listar_unidades():
    unidades = UnidadeHospitalar.query.order_by(UnidadeHospitalar.id.desc()).all()
    return jsonify([unidade.to_dict() for unidade in unidades])


@unidades_bp.route("/<int:unidade_id>", methods=["GET"])
def detalhar_unidade(unidade_id: int):
    unidade = db.session.get(UnidadeHospitalar, unidade_id)
    if not unidade:
        return jsonify({"erro": "Unidade nao encontrada"}), 404
    return jsonify(unidade.to_dict())


@unidades_bp.route("/<int:unidade_id>/turnos", methods=["GET"])
def listar_turnos_da_unidade(unidade_id: int):
    unidade = db.session.get(UnidadeHospitalar, unidade_id)
    if not unidade:
        return jsonify({"erro": "Unidade nao encontrada"}), 404

    turnos = Turno.query.filter_by(unidade_id=unidade_id).order_by(Turno.id.desc()).all()
    return jsonify({"unidade": unidade.to_dict(), "turnos": [turno.to_dict() for turno in turnos]})