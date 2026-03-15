from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.posts import posts_bp
from app.posts.forms import PostForm, CommentForm
from app.models import Post, Comment


@posts_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('posts/index.html', title='Всі записи', posts=posts)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            description=form.description.data,
            body=form.body.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Blog Post posted successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('posts/create.html', title='Новий запис', form=form)


@posts_bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments.order_by(Comment.created_at.asc()).all()
    form = CommentForm()
    return render_template('posts/detail.html', title=post.title,
                           post=post, comments=comments, form=form)


@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            name=form.name.data,
            content=form.content.data,
            author=current_user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added to the Post successfully!', 'success')
    return redirect(url_for('main.index'))


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.body = form.body.data
        db.session.commit()
        flash('Запис оновлено!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/edit.html', title='Редагувати запис',
                           form=form, post=post)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Запис видалено.', 'info')
    return redirect(url_for('main.index'))


@posts_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Коментар видалено.', 'info')
    return redirect(url_for('posts.detail', post_id=post_id))
