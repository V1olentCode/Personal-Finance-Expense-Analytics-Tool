"""Application factory for the Personal Finance web application."""

import os
from pathlib import Path

from flask import Flask

from src.database import initialize_database
from src.web_routes import web


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FINANCE_SECRET_KEY", "local-development-key"),
        DATABASE=os.environ.get("FINANCE_DATABASE", str(Path("instance") / "finance.sqlite3")),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    initialize_database(app.config["DATABASE"])
    app.register_blueprint(web)

    @app.errorhandler(413)
    def upload_too_large(_error):
        return "Upload exceeds the 5 MB limit.", 413

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
