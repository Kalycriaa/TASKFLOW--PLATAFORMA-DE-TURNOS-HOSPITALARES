from .avaliacoes import avaliacoes_bp
from .candidaturas import candidaturas_bp
from .health import health_bp
from .profissionais import profissionais_bp
from .turnos import turnos_bp
from .unidades import unidades_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(profissionais_bp)
    app.register_blueprint(unidades_bp)
    app.register_blueprint(turnos_bp)
    app.register_blueprint(candidaturas_bp)
    app.register_blueprint(avaliacoes_bp)
