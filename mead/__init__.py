from flask import Flask
from flask_login import LoginManager
from markdown2 import markdown

from mead.models import db, User, Settings
from mead.views.main import main
from mead.views.admin import admin
from mead.views.blog import blog
from mead.views.setup import setup
from mead.cli import init_db_command


def create_app():
    app = Flask(__name__)
    app.config.from_object("mead.config.Config")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Markdown filter
    @app.template_filter("markdown")
    def markdown_filter(text):
        if not text:
            return ""
        extras = ["fenced-code-blocks", "tables", "break-on-newline"]
        return markdown(text, extras=extras)
    
    # Make settings available in any page
    @app.context_processor
    def inject_settings():
        settings = Settings.query.first()
        return {"settings": settings}

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(blog)
    app.register_blueprint(setup)

    app.cli.add_command(init_db_command)

    return app


app = create_app()
