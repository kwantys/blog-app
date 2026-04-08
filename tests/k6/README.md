# k6 Навантажувальні тести — Blog App

## Встановлення k6

**Windows:**
```powershell
winget install k6 --source winget
```

**macOS:**
```bash
brew install k6
```

**Linux:**
```bash
sudo apt install k6
```

## Підготовка

1. Запустіть Flask додаток:
```bash
python run.py
```

2. Створіть тестового користувача (один раз):
Зареєструйтесь на http://localhost:5000/register з даними:
- username: `load_test_user`
- email: `load_test@example.com`
- password: `Password1!`

Також потрібен хоча б один пост (id=1) — створіть його вручну.

## Запуск тестів

```bash
cd tests/k6

# Всі 4 сценарії одночасно
k6 run load_test.js

# Окремий сценарій
k6 run scenario1_view_post.js
k6 run scenario2_comment.js
k6 run scenario3_create_post.js
k6 run scenario4_profile.js

# З HTML-звітом
k6 run --out json=results/output.json load_test.js
```

## Метрики що вимірюються

- `http_req_duration` — час від надсилання запиту до отримання останнього байту (TTLB)
- `http_req_failed` — відсоток невдалих запитів
- `vus` — кількість активних VU

## Thresholds (порогові значення)

| Метрика | Поріг |
|---------|-------|
| p(95) http_req_duration | < 600ms |
| p(99) http_req_duration | < 1200ms |
| avg http_req_duration | < 300ms |
| http_req_failed | < 1% |
