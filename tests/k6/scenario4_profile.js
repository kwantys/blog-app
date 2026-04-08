/**
 * Сценарій 4 (15%): Перегляд та редагування профілю
 * Авторизація → публічний профіль → редагування → збереження → вихід
 *
 * Метрика: http_req_duration (Time to Last Byte)
 */
import http from 'k6/http';
import { group, check, sleep } from 'k6';
import { BASE_URL, PARAMS, getCsrfToken, login, logout, checkPage } from './helpers.js';

export const options = {
  scenarios: {
    scenario4: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
  },
  thresholds: {
    http_req_duration:                      ['p(95)<600', 'p(99)<1200'],
    http_req_failed:                        ['rate<0.01'],
    'http_req_duration{page:public_profile}': ['p(95)<400'],
    'http_req_duration{page:edit_profile}':   ['p(95)<400'],
    'http_req_duration{page:save_profile}':   ['p(95)<600'],
  },
};

const USERNAME = 'load_test_user';

export default function () {

  // ── Крок 1: Авторизація ───────────────────────────────────────
  group('Авторизація', () => {
    login(USERNAME);
    sleep(1);
  });

  // ── Крок 2: Публічний профіль ────────────────────────────────
  group('Публічний профіль', () => {
    const res = http.get(`${BASE_URL}/users/${USERNAME}`, {
      tags: { page: 'public_profile' },
    });
    checkPage(res, 'Публічний профіль', USERNAME);
    sleep(1);
  });

  // ── Крок 3: Відкрити форму редагування ───────────────────────
  group('Форма редагування профілю', () => {
    const res = http.get(`${BASE_URL}/users/settings/profile`, {
      tags: { page: 'edit_profile' },
    });
    checkPage(res, 'Редагування профілю', 'Your Profile');
    sleep(1);
  });

  // ── Крок 4: Зберегти зміни профілю ───────────────────────────
  group('Збереження профілю', () => {
    const { token } = getCsrfToken(`${BASE_URL}/users/settings/profile`);

    const res = http.post(
      `${BASE_URL}/users/settings/profile`,
      {
        csrf_token: token,
        username:   USERNAME,
        email:      'load_test@example.com',
        firstname:  'Load',
        lastname:   'Tester',
        bio:        'Користувач навантажувального тесту k6',
        age:        '25',
        gender:     'M',
        address:    '',
        website:    '',
      },
      { ...PARAMS, tags: { page: 'save_profile' } }
    );

    check(res, {
      'Профіль: статус 200':   (r) => r.status === 200,
      'Профіль: збережено':    (r) => r.body.includes('Profile updated successfully!'),
    });
    sleep(1);
  });

  // ── Крок 5: Вихід ────────────────────────────────────────────
  group('Вихід', () => {
    logout();
    sleep(1);
  });
}
