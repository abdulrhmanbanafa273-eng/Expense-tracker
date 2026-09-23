import os

from flask import Flask

from app import db


def create_app():
    """Application factory: builds and configures the Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    project_root = os.path.dirname(app.root_path)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "expense_tracker.sqlite"),
        SCHEMA_PATH=os.path.join(project_root, "schema.sql"),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from app.routes.main import main
    app.register_blueprint(main)

    return app
