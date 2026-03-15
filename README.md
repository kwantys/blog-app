# Blog App

Простий блог-додаток, розроблений як навчальний проєкт для дисципліни з тестування програмного забезпечення.

## Технологічний стек

| Компонент     | Технологія                     |
|---------------|-------------------------------|
| Мова          | Python 3.10+                  |
| Фреймворк     | Flask 3.x                     |
| ORM           | Flask-SQLAlchemy               |
| БД            | SQLite (через SQLAlchemy)      |
| Автентифікація| Flask-Login + Flask-Bcrypt     |
| Форми         | Flask-WTF / WTForms            |
| Фронтенд      | Jinja2 + Bootstrap 5           |

## Структура проєкту

```
blog_app/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── models.py            # Моделі БД: User, Post, Comment
│   ├── auth/                # Blueprint: реєстрація, вхід, скидання паролю
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── posts/               # Blueprint: CRUD записів та коментарів
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── users/               # Blueprint: профіль, налаштування
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── main/                # Blueprint: головна сторінка, error handlers
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/           # Jinja2 шаблони
│   └── static/              # CSS / JS (Bootstrap CDN)
├── config.py                # Config / TestingConfig / ProductionConfig
├── run.py                   # Точка входу
├── requirements.txt
├── .env.example
└── .gitignore
```

## Функціональні можливості

- **Реєстрація** — username, email, пароль (bcrypt)
- **Вхід / Вихід** — session-based (Flask-Login), "Запам'ятати мене"
- **Скидання паролю** — токен через URLSafeTimedSerializer (email або консоль у dev-режимі)
- **Записи (Posts)** — створення, перегляд, редагування, видалення (тільки автор)
- **Коментарі** — додавання до записів, видалення власних
- **Профіль** — перегляд, редагування (username / email / bio), зміна паролю
- **Пагінація** — на головній, списку записів та профілі
- **Error pages** — 403 / 404 / 500

## Запуск

### 1. Клонувати репозиторій

```bash
git clone <repo-url>
cd blog_app
```

### 2. Створити та активувати virtualenv

```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Встановити залежності

```bash
pip install -r requirements.txt
```

### 4. Налаштувати змінні середовища

```bash
cp .env.example .env
# Відредагуйте .env — встановіть SECRET_KEY
```

### 5. Запустити

```bash
python run.py
```

Додаток доступний за адресою: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Скидання паролю (dev-режим)

Якщо `MAIL_SERVER` не вказано у `.env`, посилання для скидання паролю виводиться у консоль:

```
[DEV] Password reset link: http://127.0.0.1:5000/auth/reset-password/<token>
```

## Запуск тестів

```bash
pytest
```

> Тестова конфігурація використовує SQLite in-memory та відключає CSRF.
> Клас `TestingConfig` знаходиться у `config.py`.

## URL-маршрути

| URL                              | Опис                        |
|----------------------------------|-----------------------------|
| `/`                              | Головна (список записів)    |
| `/auth/register`                 | Реєстрація                  |
| `/auth/login`                    | Вхід                        |
| `/auth/logout`                   | Вихід                       |
| `/auth/forgot-password`          | Запит скидання паролю       |
| `/auth/reset-password/<token>`   | Форма нового паролю         |
| `/posts/`                        | Всі записи                  |
| `/posts/create`                  | Новий запис                 |
| `/posts/<id>`                    | Деталь запису + коментарі   |
| `/posts/<id>/edit`               | Редагувати запис            |
| `/posts/<id>/delete`             | Видалити запис              |
| `/posts/comment/<id>/delete`     | Видалити коментар           |
| `/users/<username>`              | Профіль користувача         |
| `/users/settings/profile`        | Редагувати профіль          |
| `/users/settings/password`       | Змінити пароль              |
