/**
 * load_test.js — Запуск усіх 4 сценаріїв одночасно
 *
 * Використання:
 *   k6 run load_test.js
 *
 * Нормальне навантаження: 5 VU на кожен сценарій = 20 VU сукупно
 * Тривалість: 30 секунд
 */
import { group, sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';
import { BASE_URL, PARAMS, getCsrfToken, login, logout, checkPage } from './helpers.js';

// ── Конфігурація навантаження ──────────────────────────────────────
export const options = {
  scenarios: {
    // Сценарій 1: Авторизація + перегляд поста + вихід
    view_post: {
      executor:        'constant-vus',
      vus:             5,
      duration:        '30s',
      exec:            'scenarioViewPost',
      tags:            { scenario: 'view_post' },
    },
    // Сценарій 2: Авторизація + два пости + коментар + вихід
    comment_post: {
      executor:        'constant-vus',
      vus:             5,
      duration:        '30s',
      exec:            'scenarioCommentPost',
      tags:            { scenario: 'comment_post' },
      startTime:       '0s',
    },
    // Сценарій 3: Авторизація + створення поста + вихід
    create_post: {
      executor:        'constant-vus',
      vus:             5,
      duration:        '30s',
      exec:            'scenarioCreatePost',
      tags:            { scenario: 'create_post' },
      startTime:       '0s',
    },
    // Сценарій 4: Авторизація + профіль + редагування + вихід
    edit_profile: {
      executor:        'constant-vus',
      vus:             5,
      duration:        '30s',
      exec:            'scenarioEditProfile',
      tags:            { scenario: 'edit_profile' },
      startTime:       '0s',
    },
  },

  // ── Порогові значення (thresholds) ──────────────────────────────
  thresholds: {
    // Загальний час відповіді
    'http_req_duration':                          ['p(95)<600', 'p(99)<1200', 'avg<300'],
    // Відсоток відмов — не більше 1%
    'http_req_failed':                            ['rate<0.01'],
    // По сценаріях
    'http_req_duration{scenario:view_post}':      ['p(95)<500'],
    'http_req_duration{scenario:comment_post}':   ['p(95)<600'],
    'http_req_duration{scenario:create_post}':    ['p(95)<700'],
    'http_req_duration{scenario:edit_profile}':   ['p(95)<600'],
  },
};

// ══════════════════════════════════════════════════════════════════
//  СЦЕНАРІЙ 1: Авторизація → Перегляд поста → Вихід
// ══════════════════════════════════════════════════════════════════
export function scenarioViewPost() {
  group('S1: Головна сторінка', () => {
    const res = http.get(`${BASE_URL}/`);
    checkPage(res, 'Головна', 'Blog App');
    sleep(1);
  });

  group('S1: Авторизація', () => {
    login();
    sleep(1);
  });

  group('S1: Перегляд поста', () => {
    const res = http.get(`${BASE_URL}/posts/1`);
    check(res, {
      'S1 пост: статус 200 або 404': (r) => r.status === 200 || r.status === 404,
    });
    sleep(2);
  });

  group('S1: Вихід', () => {
    logout();
    sleep(1);
  });
}

// ══════════════════════════════════════════════════════════════════
//  СЦЕНАРІЙ 2: Авторизація → Два пости → Коментар → Вихід
// ══════════════════════════════════════════════════════════════════
export function scenarioCommentPost() {
  group('S2: Авторизація', () => {
    login();
    sleep(1);
  });

  group('S2: Перший пост', () => {
    const res = http.get(`${BASE_URL}/posts/1`);
    check(res, { 'S2 пост1: 200/404': (r) => [200, 404].includes(r.status) });
    sleep(2);
  });

  group('S2: Повернення на головну', () => {
    const res = http.get(`${BASE_URL}/`);
    checkPage(res, 'Головна', 'Blog App');
    sleep(1);
  });

  group('S2: Другий пост + коментар', () => {
    const { token } = getCsrfToken(`${BASE_URL}/posts/1`);
    const res = http.post(
      `${BASE_URL}/posts/1/comment`,
      { csrf_token: token, name: 'k6 Tester', content: `Навантаження k6 ${Date.now()}` },
      PARAMS
    );
    check(res, {
      'S2 коментар: 200': (r) => r.status === 200,
      'S2 коментар: OK':  (r) => r.body.includes('Comment added'),
    });
    sleep(1);
  });

  group('S2: Вихід', () => {
    logout();
    sleep(1);
  });
}

// ══════════════════════════════════════════════════════════════════
//  СЦЕНАРІЙ 3: Авторизація → Створення поста → Вихід
// ══════════════════════════════════════════════════════════════════
export function scenarioCreatePost() {
  group('S3: Авторизація', () => {
    login();
    sleep(1);
  });

  group('S3: Форма нового поста', () => {
    const res = http.get(`${BASE_URL}/posts/create`);
    checkPage(res, 'Форма', 'Add a Blog/Post');
    sleep(1);
  });

  group('S3: Публікація поста', () => {
    const { token } = getCsrfToken(`${BASE_URL}/posts/create`);
    const id = randomString(4);
    const res = http.post(
      `${BASE_URL}/posts/create`,
      {
        csrf_token:  token,
        title:       `k6 Post ${id}`,
        description: 'Тест навантаження',
        body:        `Пост від k6 VU ${__VU} ітерація ${__ITER}`,
      },
      PARAMS
    );
    check(res, {
      'S3 пост: 200':        (r) => r.status === 200,
      'S3 пост: опублік.':   (r) => r.body.includes('Blog Post posted successfully!'),
    });
    sleep(1);
  });

  group('S3: Вихід', () => {
    logout();
    sleep(1);
  });
}

// ══════════════════════════════════════════════════════════════════
//  СЦЕНАРІЙ 4: Авторизація → Профіль → Редагування → Вихід
// ══════════════════════════════════════════════════════════════════
export function scenarioEditProfile() {
  const username = 'load_test_user';

  group('S4: Авторизація', () => {
    login(username);
    sleep(1);
  });

  group('S4: Публічний профіль', () => {
    const res = http.get(`${BASE_URL}/users/${username}`);
    checkPage(res, 'Профіль', username);
    sleep(1);
  });

  group('S4: Форма редагування', () => {
    const res = http.get(`${BASE_URL}/users/settings/profile`);
    checkPage(res, 'Редагування', 'Your Profile');
    sleep(1);
  });

  group('S4: Збереження профілю', () => {
    const { token } = getCsrfToken(`${BASE_URL}/users/settings/profile`);
    const res = http.post(
      `${BASE_URL}/users/settings/profile`,
      {
        csrf_token: token,
        username:   username,
        email:      'load_test@example.com',
        firstname:  'Load',
        lastname:   'Tester',
        bio:        `k6 VU${__VU}`,
        age:        '25',
        gender:     'M',
        address:    '',
        website:    '',
      },
      PARAMS
    );
    check(res, {
      'S4 профіль: 200':    (r) => r.status === 200,
      'S4 профіль: збереж': (r) => r.body.includes('Profile updated successfully!'),
    });
    sleep(1);
  });

  group('S4: Вихід', () => {
    logout();
    sleep(1);
  });
}
