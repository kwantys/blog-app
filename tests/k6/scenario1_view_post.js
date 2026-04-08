/**
 * Сценарій 1 (15%): Перегляд посту
 * Користувач авторизується → переглядає останній пост → виходить
 *
 * Метрика: http_req_duration (Time to Last Byte)
 * Успішний результат: сервер повернув повну HTML-відповідь зі статусом 200
 */
import http from 'k6/http';
import { group, sleep } from 'k6';
import { BASE_URL, login, logout, checkPage } from './helpers.js';

export const options = {
  scenarios: {
    scenario1: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
  },
  thresholds: {
    http_req_duration:            ['p(95)<500', 'p(99)<1000'],
    http_req_failed:              ['rate<0.01'],
    'http_req_duration{page:home}':  ['p(95)<400'],
    'http_req_duration{page:post}':  ['p(95)<500'],
  },
};

export default function () {

  // ── Крок 1: Головна сторінка ──────────────────────────────────
  group('Головна сторінка', () => {
    const res = http.get(`${BASE_URL}/`, {
      tags: { page: 'home' },
    });
    checkPage(res, 'Головна', 'Blog App');
    sleep(1);
  });

  // ── Крок 2: Авторизація ───────────────────────────────────────
  group('Авторизація', () => {
    login();
    sleep(1);
  });

  // ── Крок 3: Відкрити перший пост ─────────────────────────────
  group('Перегляд поста', () => {
    const res = http.get(`${BASE_URL}/posts/1`, {
      tags: { page: 'post' },
    });
    checkPage(res, 'Деталь поста', 'comments');
    sleep(2);
  });

  // ── Крок 4: Вихід ────────────────────────────────────────────
  group('Вихід', () => {
    logout();
    sleep(1);
  });
}
