from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.users import users_bp
from app.users.forms import EditProfileForm, ChangePasswordForm
from app.models import User, Post


@users_bp.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    return render_template('users/profile.html', title=f'Profile — {user.username}',
                           user=user, posts=posts)


@users_bp.route('/profile')
@login_required
def my_profile():
    """Alias: /users/profile → edit profile page (matches BasePage.PROFILE_LINK)."""
    return redirect(url_for('users.edit_profile'))


@users_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        current_user.bio = form.bio.data or ''
        current_user.firstname = form.firstname.data or ''
        current_user.lastname = form.lastname.data or ''
        current_user.age = form.age.data or ''
        current_user.gender = form.gender.data or ''
        current_user.address = form.address.data or ''
        current_user.website = form.website.data or ''
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('users/edit_profile.html', title='Your Profile', form=form)


@users_bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Поточний пароль невірний.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('users.edit_profile'))

    return render_template('users/change_password.html', title='Change Password', form=form)