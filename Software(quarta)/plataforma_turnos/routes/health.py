from flask import Blueprint, current_app, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.route("/")
def home():
    return jsonify(
        {
            "status": "ok",
            "mensagem": "API da plataforma hospitalar online",
            "location_provider": current_app.config.get("LOCATION_PROVIDER"),
        }
    )
