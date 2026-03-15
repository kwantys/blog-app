"""
UNIT tests for app/posts/routes.py (Controller layer).
Covers: create, read, edit, delete posts and comments.
Target: 50%+ coverage of posts routes.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.models import Post, Comment, User
from app import db
from tests.conftest import login_as


class TestPostListRoute:
    """Tests for GET /posts/."""

    def test_posts_index_loads(self, client):
        """GET /posts/ returns 200."""
        r = client.get('/posts/')
        assert r.status_code == 200

    def test_posts_index_shows_posts(self, client, db, sample_post):
        """Posts page lists existing posts."""
        r = client.get('/posts/')
        assert b'Test Post' in r.data


class TestPostCreateRoute:
    """Tests for GET/POST /posts/create."""

    def test_create_requires_login(self, client):
        """Unauthenticated user redirected to login."""
        r = client.get('/posts/create', follow_redirects=False)
        assert r.status_code == 302

    def test_create_page_loads_for_logged_in(self, client, db, sample_user):
        """Authenticated user can access create page."""
        login_as(client, sample_user.id)
        r = client.get('/posts/create')
        assert r.status_code == 200

    def test_create_post_success(self, client, db, sample_user):
        """Valid post data creates a new post."""
        login_as(client, sample_user.id)
        r = client.post('/posts/create', data={
            'title': 'My New Post',
            'description': 'A short description',
            'body': 'The full body content here.',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Blog Post posted successfully!' in r.data
        assert Post.query.filter_by(title='My New Post').first() is not None

    def test_create_post_missing_title(self, client, db, sample_user):
        """Post without title fails validation."""
        login_as(client, sample_user.id)
        r = client.post('/posts/create', data={
            'title': '',
            'description': 'desc',
            'body': 'body content here.',
        }, follow_redirects=True)
        assert Post.query.count() == 0

    def test_create_post_sets_correct_author(self, client, db, sample_user):
        """Created post has correct author."""
        login_as(client, sample_user.id)
        client.post('/posts/create', data={
            'title': 'Author Test',
            'description': 'desc',
            'body': 'body content here.',
        }, follow_redirects=True)
        post = Post.query.filter_by(title='Author Test').first()
        assert post is not None
        assert post.author_id == sample_user.id


class TestPostDetailRoute:
    """Tests for GET /posts/<id>."""

    def test_post_detail_loads(self, client, db, sample_post):
        """Existing post detail page returns 200."""
        r = client.get(f'/posts/{sample_post.id}')
        assert r.status_code == 200
        assert b'Test Post' in r.data

    def test_post_detail_shows_description(self, client, db, sample_post):
        """Post detail shows description."""
        r = client.get(f'/posts/{sample_post.id}')
        assert b'Short desc' in r.data

    def test_post_detail_404_for_missing(self, client, db):
        """Non-existent post returns 404."""
        r = client.get('/posts/9999')
        assert r.status_code == 404

    def test_post_detail_shows_comments(self, client, db, sample_post, sample_comment):
        """Post detail shows existing comments."""
        r = client.get(f'/posts/{sample_post.id}')
        assert b'Nice post!' in r.data


class TestPostEditRoute:
    """Tests for GET/POST /posts/<id>/edit."""

    def test_edit_requires_login(self, client, db, sample_post):
        """Unauthenticated user is redirected."""
        r = client.get(f'/posts/{sample_post.id}/edit')
        assert r.status_code == 302

    def test_edit_by_author_success(self, client, db, sample_post, sample_user):
        """Author can edit own post."""
        login_as(client, sample_user.id)
        r = client.post(f'/posts/{sample_post.id}/edit', data={
            'title': 'Updated Title',
            'description': 'Updated desc',
            'body': 'Updated body content here.',
        }, follow_redirects=True)
        assert r.status_code == 200
        db.session.expire_all()
        updated = db.session.get(Post, sample_post.id)
        assert updated.title == 'Updated Title'

    def test_edit_by_non_author_returns_403(self, client, db, sample_post, second_user):
        """Non-author gets 403 when trying to edit."""
        login_as(client, second_user.id)
        r = client.post(f'/posts/{sample_post.id}/edit', data={
            'title': 'Hacked Title',
            'description': 'desc',
            'body': 'body content here.',
        }, follow_redirects=True)
        assert r.status_code == 403


class TestPostDeleteRoute:
    """Tests for POST /posts/<id>/delete."""

    def test_delete_by_author(self, client, db, sample_post, sample_user):
        """Author can delete own post."""
        login_as(client, sample_user.id)
        r = client.post(f'/posts/{sample_post.id}/delete', follow_redirects=True)
        assert r.status_code == 200
        assert Post.query.count() == 0

    def test_delete_by_non_author_returns_403(self, client, db, sample_post, second_user):
        """Non-author gets 403 on delete attempt."""
        login_as(client, second_user.id)
        r = client.post(f'/posts/{sample_post.id}/delete', follow_redirects=True)
        assert r.status_code == 403
        assert Post.query.count() == 1

    def test_delete_requires_login(self, client, db, sample_post):
        """Unauthenticated delete is redirected."""
        r = client.post(f'/posts/{sample_post.id}/delete')
        assert r.status_code == 302


class TestCommentRoutes:
    """Tests for comment add/delete."""

    def test_add_comment_success(self, client, db, sample_post, sample_user):
        """Logged-in user can add a comment."""
        login_as(client, sample_user.id)
        r = client.post(f'/posts/{sample_post.id}/comment', data={
            'name': 'Tester',
            'content': 'Great article!',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Comment added to the Post successfully!' in r.data
        assert Comment.query.count() == 1

    def test_add_comment_requires_login(self, client, db, sample_post):
        """Unauthenticated comment attempt is redirected."""
        r = client.post(f'/posts/{sample_post.id}/comment', data={
            'name': 'X',
            'content': 'hi',
        })
        assert r.status_code == 302

    def test_add_comment_to_missing_post(self, client, db, sample_user):
        """Comment on non-existent post returns 404."""
        login_as(client, sample_user.id)
        r = client.post('/posts/9999/comment', data={
            'name': 'X',
            'content': 'hi',
        })
        assert r.status_code == 404

    def test_delete_own_comment(self, client, db, sample_comment, sample_user):
        """Author can delete own comment."""
        login_as(client, sample_user.id)
        r = client.post(f'/posts/comment/{sample_comment.id}/delete',
                        follow_redirects=True)
        assert r.status_code == 200
        assert Comment.query.count() == 0

    def test_delete_comment_by_non_author_returns_403(
            self, client, db, sample_comment, second_user):
        """Non-author gets 403 when deleting comment."""
        login_as(client, second_user.id)
        r = client.post(f'/posts/comment/{sample_comment.id}/delete',
                        follow_redirects=True)
        assert r.status_code == 403
        assert Comment.query.count() == 1