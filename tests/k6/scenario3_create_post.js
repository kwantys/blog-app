/**
 * Сценарій 3 (15%): Створення нового поста
 * Авторизація → форма нового поста → публікація → вихід
 *
 * Метрика: http_req_duration (Time to Last Byte)
 */
import http from 'k6/http';
import { group, check, sleep } from 'k6';
import { BASE_URL, PARAMS, getCsrfToken, login, logout, checkPage } from './helpers.js';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  scenarios: {
    scenario3: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
  },
  thresholds: {
    http_req_duration:                    ['p(95)<700', 'p(99)<1500'],
    http_req_failed:                      ['rate<0.01'],
    'http_req_duration{page:create_form}': ['p(95)<400'],
    'http_req_duration{page:create_post}': ['p(95)<700'],
  },
};

export default function () {

  // ── Крок 1: Авторизація ───────────────────────────────────────
  group('Авторизація', () => {
    login();
    sleep(1);
  });

  // ── Крок 2: Відкрити форму нового поста ──────────────────────
  group('Форма нового поста', () => {
    const res = http.get(`${BASE_URL}/posts/create`, {
      tags: { page: 'create_form' },
    });
    checkPage(res, 'Форма створення', 'Add a Blog/Post');
    sleep(1);
  });

  // ── Крок 3: Відправити форму (створити пост) ─────────────────
  group('Публікація поста', () => {
    const { token } = getCsrfToken(`${BASE_URL}/posts/create`);
    const uniqueId  = randomString(6);

    const res = http.post(
      `${BASE_URL}/posts/create`,
      {
        csrf_token:  token,
        title:       `k6 Load Test Post ${uniqueId}`,
        description: 'Автоматично створений пост під час навантажувального тесту',
        body:        'Цей пост створено інструментом k6 для перевірки продуктивності Flask Blog App під навантаженням 5 VU.',
      },
      { ...PARAMS, tags: { page: 'create_post' } }
    );

    check(res, {
      'Пост: статус 200':    (r) => r.status === 200,
      'Пост: опублікований': (r) => r.body.includes('Blog Post posted successfully!'),
    });
    sleep(1);
  });

  // ── Крок 4: Вихід ────────────────────────────────────────────
  group('Вихід', () => {
    logout();
    sleep(1);
  });
}
