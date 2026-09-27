import os

from flask import Flask, g, session

from app import db
from app.models.user import get_user_by_id


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

    from app.services.csrf import generate_csrf_token
    app.jinja_env.globals["csrf_token"] = generate_csrf_token

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = get_user_by_id(user_id) if user_id is not None else None

    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.transactions import transactions
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(transactions)

    return app
