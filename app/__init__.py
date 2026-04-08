from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
    login_manager.login_message_category = 'warning'

    from app.auth import auth_bp
    from app.posts import posts_bp
    from app.users import users_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(users_bp, url_prefix='/users')

    # ── ВИПРАВЛЕННЯ: Security Headers ─────────────────────────────
    # Закриває знахідки OWASP ZAP:
    #   - X-Content-Type-Options (CWE-693)
    #   - X-Frame-Options / Clickjacking (CWE-1021)
    #   - Content-Security-Policy (CWE-693)
    #   - Referrer-Policy (CWE-116)
    #   - Server header information disclosure
    @app.after_request
    def set_security_headers(response):
        # Забороняє MIME-sniffing браузером
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Захист від Clickjacking — фрейм дозволений тільки з того ж домену
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Content Security Policy — забороняє inline scripts з зовнішніх джерел
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "frame-ancestors 'self';"
        )

        # Контролює що передається у Referer header
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Захист для старих браузерів від reflected XSS
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Прибираємо Server header щоб не розкривати версію Werkzeug/Python
        response.headers['Server'] = 'Blog App'

        return response
    # ──────────────────────────────────────────────────────────────

    with app.app_context():
        db.create_all()

    return app