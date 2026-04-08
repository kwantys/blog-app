import logging
from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from app import db
from app.auth import auth_bp
from app.auth.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.models import User

logger = logging.getLogger(__name__)


def is_safe_url(target: str) -> bool:
    """
    Перевіряє що URL є відносним і належить тому ж хосту.
    Захищає від CWE-601 (Open Redirect).

    Приклади:
        is_safe_url('/posts/1')          → True
        is_safe_url('https://evil.com')  → False
        is_safe_url('//evil.com/path')   → False
    """
    ref_url  = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Користувач з таким email або іменем вже існує.', 'danger')
            return render_template('auth/register.html', title='Реєстрація', form=form)
        login_user(user)
        flash('Congrats! Your registration has been successful.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', title='Реєстрація', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            # ── ВИПРАВЛЕННЯ CWE-601: валідація next_page ──────────────
            # До виправлення: next_page використовувався без перевірки,
            # що дозволяло атаку /login?next=https://evil.com
            next_page = request.args.get('next')
            if next_page and not is_safe_url(next_page):
                logger.warning('Blocked unsafe redirect to: %s', next_page)
                next_page = None
            # ──────────────────────────────────────────────────────────

            flash(f'Ласкаво просимо, {user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Невірний username або пароль.', 'danger')

    return render_template('auth/login.html', title='Вхід', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            mail_server = current_app.config.get('MAIL_SERVER')
            if mail_server:
                _send_reset_email(user, reset_url)
            else:
                logger.warning('[DEV] Password reset link for %s: %s',
                               user.email, reset_url)
        flash('Якщо такий email зареєстровано, посилання для скидання паролю '
              'буде надіслано.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Забули пароль?', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_token(token)
    if not user:
        flash('Посилання для скидання паролю недійсне або прострочене.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль успішно змінено. Тепер ви можете увійти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Скинути пароль', form=form)


def _send_reset_email(user, reset_url):
    """Надсилає email для скидання паролю."""
    try:
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        msg = Message(
            subject='Скидання паролю — Blog App',
            recipients=[user.email],
            body=(
                f'Для скидання паролю перейдіть за посиланням:\n{reset_url}\n\n'
                f'Якщо ви не надсилали цей запит, просто ігноруйте листа.'
            ),
        )
        mail.send(msg)
    except Exception as e:
        logger.error('Failed to send reset email: %s', e)