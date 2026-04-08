"""
seed_data.py — Наповнення БД тестовими даними перед стрес-тестом.

Мета: додати 1000+ постів та коментарів щоб перегляд
першого поста та 1000-го використовував однакову кількість ресурсів.

Запуск з кореня проекту:
    python tests/k6/seed_data.py

Або з параметрами:
    python tests/k6/seed_data.py --users 10 --posts 500 --comments 2000
"""
import sys
import os
import argparse
import random
from datetime import datetime, timezone, timedelta

# Додаємо корінь проекту до шляху
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app, db
from app.models import User, Post, Comment
from config import Config


# ── Конфігурація ───────────────────────────────────────────────────
DEFAULT_USERS    = 10
DEFAULT_POSTS    = 500
DEFAULT_COMMENTS = 2000

STRESS_USERS = [
    {'username': 'stress_user1', 'email': 'stress1@example.com'},
    {'username': 'stress_user2', 'email': 'stress2@example.com'},
    {'username': 'stress_user3', 'email': 'stress3@example.com'},
    {'username': 'stress_user4', 'email': 'stress4@example.com'},
    {'username': 'stress_user5', 'email': 'stress5@example.com'},
    {'username': 'load_test_user', 'email': 'load_test@example.com'},
]

SAMPLE_TITLES = [
    "Розробка на Python: поради початківцям",
    "Як налаштувати Flask для продакшену",
    "SQLAlchemy ORM: продуктивні запити",
    "Тестування веб-додатків: від unit до e2e",
    "Docker та Flask: покроковий гайд",
    "JavaScript для бекенд-розробника",
    "REST API: кращі практики",
    "Автоматизація тестування з pytest",
    "Навантажувальне тестування з k6",
    "Git workflow для команди розробників",
]

SAMPLE_BODIES = [
    "Це детальна стаття про тему. " * 50,
    "Сучасний підхід до розробки передбачає... " * 40,
    "Для початку розглянемо основні концепції. " * 60,
    "Практичний приклад допоможе краще зрозуміти матеріал. " * 45,
]

SAMPLE_COMMENTS = [
    "Чудова стаття, дуже корисно!",
    "Дякую за детальне пояснення.",
    "Маю питання щодо третього пункту.",
    "Використав цей підхід у своєму проекті — відмінно.",
    "Можна додати більше прикладів?",
    "Цінна інформація, збережу для себе.",
]


def parse_args():
    parser = argparse.ArgumentParser(description='Seed Blog App database')
    parser.add_argument('--users',    type=int, default=DEFAULT_USERS)
    parser.add_argument('--posts',    type=int, default=DEFAULT_POSTS)
    parser.add_argument('--comments', type=int, default=DEFAULT_COMMENTS)
    parser.add_argument('--clean',    action='store_true',
                        help='Видалити існуючі seed-дані перед додаванням')
    return parser.parse_args()


def create_stress_users(app):
    """Створює фіксованих користувачів для стрес-тесту."""
    users = []
    with app.app_context():
        for ud in STRESS_USERS:
            u = User.query.filter_by(username=ud['username']).first()
            if not u:
                u = User(username=ud['username'], email=ud['email'])
                u.set_password('Password1!')
                db.session.add(u)
                print(f"  Створено: {ud['username']}")
            else:
                print(f"  Існує:    {ud['username']}")
            users.append(u)
        db.session.commit()
    return users


def create_seed_users(app, count):
    """Створює додаткових seed-користувачів."""
    users = []
    with app.app_context():
        for i in range(count):
            username = f'seed_user_{i:04d}'
            u = User.query.filter_by(username=username).first()
            if not u:
                u = User(
                    username=username,
                    email=f'seed_{i:04d}@example.com'
                )
                u.set_password('Password1!')
                db.session.add(u)
            users.append(u)
        db.session.commit()
        print(f"  Користувачів у БД: {User.query.count()}")
    return users


def create_seed_posts(app, post_count, users):
    """Створює тестові пости рівномірно розподілені у часі."""
    print(f"\nСтворення {post_count} постів...")
    with app.app_context():
        # Перезавантажуємо users у поточному контексті
        user_ids = [u.id for u in User.query.limit(len(users)).all()]
        if not user_ids:
            print("  Помилка: немає користувачів!")
            return

        batch_size = 100
        created = 0
        base_time = datetime.now(timezone.utc) - timedelta(days=180)

        for i in range(post_count):
            title_base = random.choice(SAMPLE_TITLES)
            author_id  = random.choice(user_ids)
            created_at = base_time + timedelta(
                seconds=random.randint(0, 180 * 24 * 3600)
            )

            post = Post(
                title       = f"{title_base} #{i:04d}",
                description = f"Опис поста номер {i}. Тестові дані для навантажувального тесту.",
                body        = random.choice(SAMPLE_BODIES) + f" (Post #{i})",
                author_id   = author_id,
                created_at  = created_at,
            )
            db.session.add(post)
            created += 1

            if created % batch_size == 0:
                db.session.commit()
                print(f"  {created}/{post_count} постів...", end='\r')

        db.session.commit()
        print(f"\n  Постів у БД: {Post.query.count()}")


def create_seed_comments(app, comment_count):
    """Створює тестові коментарі до існуючих постів."""
    print(f"\nСтворення {comment_count} коментарів...")
    with app.app_context():
        post_ids   = [p.id for p in Post.query.with_entities(Post.id).all()]
        user_ids   = [u.id for u in User.query.with_entities(User.id).all()]

        if not post_ids or not user_ids:
            print("  Немає постів або користувачів для коментарів!")
            return

        batch_size = 200
        created = 0

        for i in range(comment_count):
            comment = Comment(
                name      = f"Seed Commenter {i % 20}",
                content   = random.choice(SAMPLE_COMMENTS) + f" (#{i})",
                author_id = random.choice(user_ids),
                post_id   = random.choice(post_ids),
            )
            db.session.add(comment)
            created += 1

            if created % batch_size == 0:
                db.session.commit()
                print(f"  {created}/{comment_count} коментарів...", end='\r')

        db.session.commit()
        print(f"\n  Коментарів у БД: {Comment.query.count()}")


def main():
    args = parse_args()
    app = create_app(Config)

    print("=" * 50)
    print("  Blog App — Seed Data Generator")
    print("=" * 50)
    print(f"  Планується: {args.users} користувачів, {args.posts} постів, {args.comments} коментарів")

    # 1. Стрес-користувачі (фіксовані)
    print("\n1. Стрес-користувачі:")
    create_stress_users(app)

    # 2. Додаткові seed-користувачі
    print(f"\n2. Seed-користувачі ({args.users}):")
    seed_users = create_seed_users(app, args.users)

    # 3. Пости
    all_users = seed_users
    create_seed_posts(app, args.posts, all_users)

    # 4. Коментарі
    create_seed_comments(app, args.comments)

    print("\n" + "=" * 50)
    print("  Seed data створено успішно!")
    with app.app_context():
        print(f"  Підсумок БД:")
        print(f"    Users:    {User.query.count()}")
        print(f"    Posts:    {Post.query.count()}")
        print(f"    Comments: {Comment.query.count()}")
    print("=" * 50)


if __name__ == '__main__':
    main()
