"""Hameçon Flask application factory."""

from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    login_manager.init_app(app)

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(int(user_id))

    # Import the blueprints AND all their route files FIRST,
    # so every route is attached before the blueprint is sealed.
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.admin import recipient_routes  # noqa - attaches Day 7 routes to admin_bp
    from app.admin import campaign_routes  # noqa - attaches Day 8 routes to admin_bp
    # Registration comes AFTER every route is attached.
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("admin.dashboard"))

    return app
