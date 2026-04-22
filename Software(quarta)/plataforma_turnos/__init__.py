from flask import Flask

from config import Config

from .extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401
    from .routes import register_blueprints

    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app
