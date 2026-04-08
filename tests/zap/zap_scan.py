"""
zap_scan.py — Автоматизований запуск OWASP ZAP через Python API.

Передумови:
    1. ZAP запущено у daemon-режимі:
       zap.sh -daemon -port 8090 -config api.disablekey=true
    2. Додаток запущено: python run.py
    3. Тестовий користувач існує: zap_test_user / Password1!

Запуск:
    python tests/zap/zap_scan.py
"""
import time
import sys

try:
    from zapv2 import ZAPv2
except ImportError:
    print("Встановіть: pip install python-owasp-zap-v2.4")
    sys.exit(1)

TARGET  = 'http://localhost:5000'
ZAP_URL = 'http://localhost:8090'

USERNAME = 'zap_test_user'
PASSWORD = 'Password1!'


def main():
    zap = ZAPv2(proxies={'http': ZAP_URL, 'https': ZAP_URL})

    print(f'[1/6] ZAP версія: {zap.core.version}')

    # ── 1. Налаштування контексту ─────────────────────────────────
    ctx_id = zap.context.new_context('BlogApp')
    zap.context.include_in_context('BlogApp', f'{TARGET}.*')
    zap.context.exclude_from_context('BlogApp', f'{TARGET}/auth/logout')
    print('[2/6] Контекст створено')

    # ── 2. Налаштування аутентифікації ────────────────────────────
    # Форма входу: POST /auth/login з полями username, password, csrf_token
    login_url = f'{TARGET}/auth/login'
    login_data = 'username={%username%}&password={%password%}'

    zap.authentication.set_authentication_method(
        ctx_id,
        'formBasedAuthentication',
        f'loginUrl={login_url}&loginRequestData={login_data}'
    )
    zap.authentication.set_logged_in_indicator(ctx_id, r'\Qid="log_out"\E')
    zap.authentication.set_logged_out_indicator(ctx_id, r'\QSign In\E')

    # ── 3. Додавання тестового користувача ────────────────────────
    user_id = zap.users.new_user(ctx_id, USERNAME)
    zap.users.set_authentication_credentials(
        ctx_id, user_id,
        f'username={USERNAME}&password={PASSWORD}'
    )
    zap.users.set_user_enabled(ctx_id, user_id, True)
    zap.forcedUser.set_forced_user(ctx_id, user_id)
    zap.forcedUser.set_forced_user_mode_enabled(True)
    print(f'[3/6] Користувач {USERNAME} налаштований')

    # ── 4. Spider (обхід сайту з авторизацією) ────────────────────
    print('[4/6] Spider запущено...')
    scan_id = zap.spider.scan_as_user(ctx_id, user_id, TARGET)
    while int(zap.spider.status(scan_id)) < 100:
        print(f'  Spider: {zap.spider.status(scan_id)}%', end='\r')
        time.sleep(2)
    print(f'  Spider завершено. URLs: {len(zap.spider.results(scan_id))}')

    # ── 5. Активне сканування ─────────────────────────────────────
    print('[5/6] Активне сканування...')
    ascan_id = zap.ascan.scan_as_user(TARGET, ctx_id, user_id, True)
    while int(zap.ascan.status(ascan_id)) < 100:
        print(f'  Scan: {zap.ascan.status(ascan_id)}%', end='\r')
        time.sleep(5)
    print('  Активне сканування завершено')

    # ── 6. Генерація звіту ────────────────────────────────────────
    print('[6/6] Генерація звіту...')
    report = zap.core.htmlreport()
    with open('tests/zap/results/zap_report.html', 'w', encoding='utf-8') as f:
        f.write(report)

    # Виводимо знахідки
    alerts = zap.core.alerts(baseurl=TARGET)
    print(f'\nЗнайдено {len(alerts)} попереджень:')
    by_risk = {}
    for alert in alerts:
        risk = alert.get('risk', 'Informational')
        by_risk[risk] = by_risk.get(risk, 0) + 1

    for risk in ['High', 'Medium', 'Low', 'Informational']:
        if risk in by_risk:
            print(f'  {risk}: {by_risk[risk]}')

    print('\nЗвіт збережено: tests/zap/results/zap_report.html')


if __name__ == '__main__':
    main()
