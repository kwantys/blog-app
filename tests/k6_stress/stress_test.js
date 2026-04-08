/**
 * stress_test.js — Стрес-тест Blog App
 *
 * Стратегія: поступове збільшення VU до виявлення точки відмов
 * Фази: прогрів → норма → стрес → пік → відновлення
 *
 * Запуск: k6 run stress_test.js --out json=results/stress_output.json
 */
import http from 'k6/http';
import { group, check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { BASE_URL, PARAMS, getCsrfToken, login, logout, checkPage } from './helpers.js';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// ── Власні метрики ─────────────────────────────────────────────────
const loginErrors    = new Counter('login_errors');
const pageErrors     = new Counter('page_errors');
const postErrors     = new Counter('post_errors');
const errorRate      = new Rate('error_rate');
const loginDuration  = new Trend('login_duration',  true);
const pageDuration   = new Trend('page_duration',   true);
const postDuration   = new Trend('post_duration',   true);

// ── Конфігурація стрес-тесту ───────────────────────────────────────
export const options = {
  stages: [
    // ── ФАЗА 1: Прогрів (warm-up) — 2 хвилини ──────────────────
    { duration: '1m', target: 2  },   // плавний старт
    { duration: '1m', target: 5  },   // нормальне навантаження

    // ── ФАЗА 2: Нормальне навантаження — 2 хвилини ──────────────
    { duration: '1m', target: 10 },
    { duration: '1m', target: 10 },   // стабілізація

    // ── ФАЗА 3: Стрес — 3 хвилини ───────────────────────────────
    { duration: '1m', target: 20 },
    { duration: '1m', target: 30 },
    { duration: '1m', target: 40 },

    // ── ФАЗА 4: Пік — 2 хвилини ─────────────────────────────────
    { duration: '1m', target: 50 },
    { duration: '1m', target: 60 },

    // ── ФАЗА 5: Відновлення — 2 хвилини ─────────────────────────
    { duration: '1m', target: 10 },
    { duration: '1m', target: 0  },
  ],

  thresholds: {
    // Загальний час відповіді
    http_req_duration:   ['p(95)<2000', 'p(99)<5000'],
    http_req_failed:     ['rate<0.10'],  // допускаємо до 10% при піку
    // Власні метрики
    login_duration:      ['p(95)<1000'],
    page_duration:       ['p(95)<500'],
    post_duration:       ['p(95)<1500'],
    error_rate:          ['rate<0.10'],
  },
};

// ── Налаштування користувача ───────────────────────────────────────
const USERS = [
  { username: 'stress_user1', password: 'Password1!' },
  { username: 'stress_user2', password: 'Password1!' },
  { username: 'stress_user3', password: 'Password1!' },
  { username: 'stress_user4', password: 'Password1!' },
  { username: 'stress_user5', password: 'Password1!' },
];

function getUser() {
  return USERS[__VU % USERS.length];
}

// ── Головна функція тесту ──────────────────────────────────────────
export default function () {
  const user = getUser();

  // ── Крок 1: Головна (без авторизації) ────────────────────────
  group('Головна сторінка', () => {
    const start = Date.now();
    const res = http.get(`${BASE_URL}/`, { tags: { endpoint: 'home' } });
    pageDuration.add(Date.now() - start);

    const ok = check(res, {
      'Головна: 200': (r) => r.status === 200,
      'Головна: HTML': (r) => r.body.includes('Blog App'),
    });
    if (!ok) { pageErrors.add(1); errorRate.add(1); } else { errorRate.add(0); }
    sleep(0.5);
  });

  // ── Крок 2: Авторизація ───────────────────────────────────────
  group('Авторизація', () => {
    const start = Date.now();
    const { token } = getCsrfToken(`${BASE_URL}/auth/login`);
    const res = http.post(
      `${BASE_URL}/auth/login`,
      { csrf_token: token, username: user.username, password: user.password },
      { ...PARAMS, tags: { endpoint: 'login' } }
    );
    loginDuration.add(Date.now() - start);

    const ok = check(res, {
      'Login: 200':     (r) => r.status === 200,
      'Login: success': (r) => r.body.includes('log_out'),
    });
    if (!ok) { loginErrors.add(1); errorRate.add(1); } else { errorRate.add(0); }
    sleep(0.5);
  });

  // ── Крок 3: Перегляд постів ───────────────────────────────────
  group('Перегляд постів', () => {
    // Список постів
    const listRes = http.get(`${BASE_URL}/`, { tags: { endpoint: 'posts_list' } });
    check(listRes, { 'Список постів: 200': (r) => r.status === 200 });

    // Деталь поста — рандомний ID від 1 до 50
    const postId = Math.ceil(Math.random() * 50);
    const start = Date.now();
    const detailRes = http.get(
      `${BASE_URL}/posts/${postId}`,
      { tags: { endpoint: 'post_detail' } }
    );
    pageDuration.add(Date.now() - start);

    check(detailRes, {
      'Деталь поста: 200/404': (r) => r.status === 200 || r.status === 404,
    });
    sleep(1);
  });

  // ── Крок 4: Створення поста (кожен 3-й VU) ───────────────────
  if (__VU % 3 === 0) {
    group('Створення поста', () => {
      const { token } = getCsrfToken(`${BASE_URL}/posts/create`);
      const start = Date.now();
      const res = http.post(
        `${BASE_URL}/posts/create`,
        {
          csrf_token:  token,
          title:       `Stress Post ${randomString(8)}`,
          description: 'Stress test post',
          body:        `Post created by VU ${__VU} iter ${__ITER} at ${Date.now()}`,
        },
        { ...PARAMS, tags: { endpoint: 'create_post' } }
      );
      postDuration.add(Date.now() - start);

      const ok = check(res, {
        'Пост: 200':  (r) => r.status === 200,
        'Пост: OK':   (r) => r.body.includes('Blog Post posted successfully!'),
      });
      if (!ok) { postErrors.add(1); errorRate.add(1); } else { errorRate.add(0); }
      sleep(0.5);
    });
  }

  // ── Крок 5: Вихід ────────────────────────────────────────────
  group('Вихід', () => {
    const res = http.get(`${BASE_URL}/auth/logout`, { tags: { endpoint: 'logout' } });
    check(res, { 'Logout: 200': (r) => r.status === 200 });
    sleep(0.5);
  });
}

// ── Підсумковий звіт ──────────────────────────────────────────────
export function handleSummary(data) {
  return {
    'results/stress_summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  };
}

function textSummary(data) {
  const m = data.metrics;
  const dur = m.http_req_duration;
  const failed = m.http_req_failed;

  return `
╔══════════════════════════════════════════════════════╗
║         STRESS TEST — ПІДСУМКОВИЙ ЗВІТ              ║
╠══════════════════════════════════════════════════════╣
║  Всього запитів:  ${String(m.http_reqs?.values?.count || 0).padEnd(32)}║
║  Відмов:          ${String(((failed?.values?.rate || 0)*100).toFixed(2)+'%').padEnd(32)}║
╠══════════════════════════════════════════════════════╣
║  http_req_duration:                                  ║
║    avg:    ${String((dur?.values?.avg || 0).toFixed(0)+'ms').padEnd(41)}║
║    median: ${String((dur?.values?.med || 0).toFixed(0)+'ms').padEnd(41)}║
║    p(90):  ${String((dur?.values?.['p(90)'] || 0).toFixed(0)+'ms').padEnd(41)}║
║    p(95):  ${String((dur?.values?.['p(95)'] || 0).toFixed(0)+'ms').padEnd(41)}║
║    p(99):  ${String((dur?.values?.['p(99)'] || 0).toFixed(0)+'ms').padEnd(41)}║
╚══════════════════════════════════════════════════════╝
`;
}
