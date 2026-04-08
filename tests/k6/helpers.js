/**
 * helpers.js — спільні утиліти для всіх k6 сценаріїв
 * CSRF-токен, авторизація, перевірки
 */
import http from 'k6/http';
import { check } from 'k6';

export const BASE_URL = 'http://localhost:5000';

export const PARAMS = {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
};

/**
 * Витягує CSRF-токен з HTML-сторінки
 */
export function getCsrfToken(url) {
  const res = http.get(url);
  const token = res.html().find('input[name="csrf_token"]').first().attr('value');
  return { res, token };
}

/**
 * Виконує вхід у систему, повертає сесійні cookies
 */
export function login(username = 'load_test_user', password = 'Password1!') {
  const { token } = getCsrfToken(`${BASE_URL}/auth/login`);

  const res = http.post(
    `${BASE_URL}/auth/login`,
    {
      csrf_token: token,
      username:   username,
      password:   password,
    },
    PARAMS
  );

  check(res, {
    'login: статус 200':          (r) => r.status === 200,
    'login: авторизація успішна':  (r) => r.body.includes('log_out'),
  });

  return res;
}

/**
 * Виконує вихід із системи
 */
export function logout() {
  const res = http.get(`${BASE_URL}/auth/logout`);
  check(res, {
    'logout: статус 200': (r) => r.status === 200,
  });
  return res;
}

/**
 * Стандартна перевірка успішного завантаження сторінки.
 * k6 вимірює http_req_duration — час від надсилання запиту
 * до отримання останнього байту відповіді (TTLB).
 */
export function checkPage(res, name, expectedText) {
  return check(res, {
    [`${name}: статус 200`]:           (r) => r.status === 200,
    [`${name}: сторінка завантажена`]: (r) => r.body.includes(expectedText),
  });
}
