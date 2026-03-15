from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app.main import main_bp
from app.models import Post


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('main/index.html', title='Dashboard', posts=posts)


# ── Short-URL aliases matching BasePage constants ──────────────────────────────
# BasePage.LOGIN_LINK     = "http://localhost:8080/login"
# BasePage.REG_LINK       = "http://localhost:8080/register"
# BasePage.PROFILE_LINK   = "http://localhost:8080/profile"
# BasePage.BLOG_POST_LINK = "http://localhost:8080/post"
# BasePage.FORGOT_PASSWORD_LINK = "http://localhost:8080/forgot"

@main_bp.route('/login', methods=['GET', 'POST'])
def login_alias():
    return redirect(url_for('auth.login'))


@main_bp.route('/register', methods=['GET', 'POST'])
def register_alias():
    return redirect(url_for('auth.register'))


@main_bp.route('/profile')
@login_required
def profile_alias():
    return redirect(url_for('users.edit_profile'))


@main_bp.route('/post', methods=['GET', 'POST'])
@login_required
def post_alias():
    return redirect(url_for('posts.create'))


@main_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_alias():
    return redirect(url_for('auth.forgot_password'))


@main_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_alias(token):
    return redirect(url_for('auth.reset_password', token=token))


# ── Error handlers ─────────────────────────────────────────────────────────────

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
