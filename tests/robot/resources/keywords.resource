*** Settings ***
Library    SeleniumLibrary
Library    String

*** Variables ***
${BASE_URL}       http://localhost:5000
${BROWSER}        chrome
${TIMEOUT}        10s
${VALID_USER}     rf_user_01
${VALID_EMAIL}    rf_user_01@example.com
${VALID_PASS}     Password1!

*** Keywords ***

# ── Браузер ────────────────────────────────────────────────────────
Відкрити браузер до додатку
    Open Browser    ${BASE_URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Timeout    ${TIMEOUT}

Закрити браузер
    Close Browser

# ── Безпечний клік (обходить перекриття елементів) ─────────────────
Безпечний клік    [Arguments]    ${locator}
    [Documentation]    Прокручує до елемента і клікає через JS щоб уникнути перекриття
    Wait Until Element Is Visible    ${locator}    ${TIMEOUT}
    Scroll Element Into View         ${locator}
    Execute Javascript    document.querySelector('${locator.replace("id=", "#").replace("css=", "")}').click()

# ── Навігація ──────────────────────────────────────────────────────
Перейти на сторінку реєстрації
    Go To    ${BASE_URL}/register

Перейти на сторінку входу
    Go To    ${BASE_URL}/login

Перейти на головну сторінку
    Go To    ${BASE_URL}/

Перейти на сторінку забули пароль
    Go To    ${BASE_URL}/forgot

Перейти на сторінку створення поста
    Go To    ${BASE_URL}/post

Перейти на профіль
    Go To    ${BASE_URL}/profile

# ── Реєстрація ─────────────────────────────────────────────────────
Зареєструвати користувача    [Arguments]    ${username}    ${email}    ${password}    ${confirm}
    Перейти на сторінку реєстрації
    Input Text       id=username    ${username}
    Input Text       id=email       ${email}
    Input Text       id=password    ${password}
    Input Text       id=confirm     ${confirm}
    Безпечний клік   id=register

# ── Вхід / Вихід ───────────────────────────────────────────────────
Увійти як    [Arguments]    ${username}    ${password}
    Перейти на сторінку входу
    Input Text       id=username    ${username}
    Input Text       id=password    ${password}
    Безпечний клік   id=login

Увійти валідним користувачем
    Увійти як    ${VALID_USER}    ${VALID_PASS}

Вийти з системи
    Безпечний клік    id=log_out

Очистити сесію
    [Documentation]    Видаляє cookies — гарантує неавторизований стан перед тестом
    Delete All Cookies
    Go To    ${BASE_URL}/

# ── Пости ──────────────────────────────────────────────────────────
Створити пост    [Arguments]    ${title}    ${description}    ${body}
    Перейти на сторінку створення поста
    Input Text       id=title          ${title}
    Input Text       id=description    ${description}
    Input Text       id=body           ${body}
    Безпечний клік   id=post

# ── Коментарі ──────────────────────────────────────────────────────
Додати коментар до поста    [Arguments]    ${post_id}    ${name}    ${message}
    Go To            ${BASE_URL}/posts/${post_id}
    Input Text       id=name       ${name}
    Input Text       id=message    ${message}
    Безпечний клік   id=add_comment

# ── Профіль ────────────────────────────────────────────────────────
Оновити профіль    [Arguments]    ${firstname}    ${lastname}    ${bio}
    Перейти на профіль
    Clear Element Text    id=firstname
    Input Text            id=firstname    ${firstname}
    Clear Element Text    id=lastname
    Input Text            id=lastname     ${lastname}
    Clear Element Text    id=bio
    Input Text            id=bio          ${bio}
    Безпечний клік        id=update_profile

# ── Перевірки ──────────────────────────────────────────────────────
Перевірити успішне повідомлення
    Wait Until Element Is Visible    id=alert_success    ${TIMEOUT}
    Element Should Be Visible        id=alert_success

Перевірити повідомлення про помилку
    Wait Until Element Is Visible    id=alert_error    ${TIMEOUT}
    Element Should Be Visible        id=alert_error

Перевірити що знаходимось на сторінці    [Arguments]    ${expected_url}
    Location Should Be    ${expected_url}

Перевірити що URL містить    [Arguments]    ${fragment}
    Location Should Contain    ${fragment}

Перевірити що сторінка містить текст    [Arguments]    ${text}
    Page Should Contain    ${text}

Перевірити що кнопка logout присутня
    Element Should Be Visible    id=log_out

Перевірити що кнопка logout відсутня
    Element Should Not Be Visible    id=log_out
