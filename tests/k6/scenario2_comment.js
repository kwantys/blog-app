/**
 * Сценарій 2 (15%): Перегляд посту та коментар
 * Авторизація → пост 1 → головна → пост 2 → коментар → вихід
 *
 * Метрика: http_req_duration (Time to Last Byte)
 */
import http from 'k6/http';
import { group, check, sleep } from 'k6';
import { BASE_URL, BASE_URL as BU, PARAMS, getCsrfToken, login, logout, checkPage } from './helpers.js';

export const options = {
  scenarios: {
    scenario2: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
  },
  thresholds: {
    http_req_duration:                    ['p(95)<600', 'p(99)<1200'],
    http_req_failed:                      ['rate<0.01'],
    'http_req_duration{page:post_detail}': ['p(95)<500'],
    'http_req_duration{page:comment}':     ['p(95)<600'],
  },
};

export default function () {

  // ── Крок 1: Авторизація ───────────────────────────────────────
  group('Авторизація', () => {
    login();
    sleep(1);
  });

  // ── Крок 2: Відкрити перший пост ─────────────────────────────
  group('Перегляд першого поста', () => {
    const res = http.get(`${BASE_URL}/posts/1`, {
      tags: { page: 'post_detail' },
    });
    checkPage(res, 'Пост 1', 'comments');
    sleep(2);
  });

  // ── Крок 3: Повернутись на головну ───────────────────────────
  group('Повернення на головну', () => {
    const res = http.get(`${BASE_URL}/`);
    checkPage(res, 'Головна', 'Blog App');
    sleep(1);
  });

  // ── Крок 4: Відкрити другий пост ─────────────────────────────
  group('Перегляд другого поста', () => {
    const res = http.get(`${BASE_URL}/posts/2`, {
      tags: { page: 'post_detail' },
    });
    // Пост 2 може не існувати — перевіряємо 200 або 404
    check(res, {
      'Пост 2: статус 200 або 404': (r) => r.status === 200 || r.status === 404,
    });
    sleep(2);
  });

  // ── Крок 5: Залишити коментар до поста 1 ─────────────────────
  group('Додавання коментаря', () => {
    // Отримуємо CSRF-токен зі сторінки поста
    const { token } = getCsrfToken(`${BASE_URL}/posts/1`);

    const res = http.post(
      `${BASE_URL}/posts/1/comment`,
      {
        csrf_token: token,
        name:       'Load Tester',
        content:    'Коментар від k6 навантажувального тесту',
      },
      { ...PARAMS, tags: { page: 'comment' } }
    );

    check(res, {
      'Коментар: статус 200':  (r) => r.status === 200,
      'Коментар: додано':      (r) => r.body.includes('Comment added'),
    });
    sleep(1);
  });

  // ── Крок 6: Вихід ────────────────────────────────────────────
  group('Вихід', () => {
    logout();
    sleep(1);
  });
}
