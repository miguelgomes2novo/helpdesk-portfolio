"""Fábrica da aplicação HelpDesk."""
from pathlib import Path
from flask import Flask
from .db import init_app as init_database
from .routes import api

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=str(Path(app.instance_path) / "chamados.sqlite3"), SEED_DEMO=True, JSON_SORT_KEYS=False)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.register_blueprint(api)
    init_database(app)
    return app
