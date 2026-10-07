from flask import Flask
from .config import Config
from .extensions import db


def create_app(test_config=None):

    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_object(Config)

    db.init_app(app)

    from .routes import certificate_bp
    app.register_blueprint(certificate_bp)

    with app.app_context():
        db.create_all()

    return app