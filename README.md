# Blog App

Простий блог-додаток, розроблений як навчальний проєкт для дисципліни з тестування програмного забезпечення.

## Технологічний стек

| Компонент      | Технологія                 |
|----------------|---------------------------|
| Мова           | Python 3.10+              |
| Фреймворк      | Flask 3.x                 |
| ORM            | Flask-SQLAlchemy           |
| БД             | SQLite (через SQLAlchemy) |
| Автентифікація | Flask-Login + Flask-Bcrypt |
| Форми          | Flask-WTF / WTForms        |
| Фронтенд       | Jinja2 + Bootstrap 5       |
| Збірка         | Make (Makefile)            |
| Тести          | pytest + pytest-flask      |
| Лінтер         | flake8                     |

## Структура проєкту

```
blog_app/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── models.py            # Моделі БД: User, Post, Comment
│   ├── auth/                # Blueprint: реєстрація, вхід, скидання паролю
│   ├── posts/               # Blueprint: CRUD записів та коментарів
│   ├── users/               # Blueprint: профіль, налаштування
│   ├── main/                # Blueprint: головна сторінка, error handlers
│   └── templates/           # Jinja2 шаблони
├── tests/                   # Тести (pytest)
├── config.py                # Config / TestingConfig / ProductionConfig
├── run.py                   # Точка входу
├── Makefile                 # Автоматизація збірки
├── requirements.txt         # Залежності
├── .env.example
└── .gitignore
```

## Швидкий старт (через Make)

```bash
git clone <repo-url>
cd blog_app
cp .env.example .env        # встановіть SECRET_KEY у .env
make install                # створює venv + встановлює залежності
make run                    # запускає додаток → http://127.0.0.1:5000
```

## Всі команди Make

| Команда        | Що робить                                    |
|----------------|----------------------------------------------|
| `make install` | Створює `.venv` та встановлює всі залежності |
| `make run`     | Запускає Flask у режимі розробки             |
| `make test`    | Запускає pytest з деталізованим виводом      |
| `make lint`    | Перевіряє код через flake8                   |
| `make clean`   | Видаляє `__pycache__`, `*.pyc`, `*.db`       |
| `make all`     | `install` + `test`                           |

## Ручний запуск (без Make)

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env        # встановіть SECRET_KEY
python run.py
```

## Запуск тестів

```bash
make test
# або без Make:
pytest tests/ -v
```

## Скидання паролю (dev-режим)

Якщо `MAIL_SERVER` не вказано у `.env`, посилання для скидання паролю виводиться у консоль:

```
[DEV] Password reset link: http://127.0.0.1:5000/auth/reset-password/<token>
```

## URL-маршрути

| URL                            | Опис                      |
|--------------------------------|---------------------------|
| `/`                            | Головна (список записів)  |
| `/login`                       | Вхід                      |
| `/register`                    | Реєстрація                |
| `/forgot`                      | Запит скидання паролю     |
| `/profile`                     | Редагувати профіль        |
| `/post`                        | Новий запис               |
| `/posts/<id>`                  | Деталь запису + коментарі |
| `/users/<username>`            | Профіль користувача       |
