*** Settings ***
Resource          resources/keywords.resource
Suite Setup       Відкрити браузер до додатку
Suite Teardown    Закрити браузер
Test Tags         blog_app

*** Variables ***
${UNIQUE_USER}    rf_user_01
${UNIQUE_EMAIL}   rf_user_01@example.com

*** Test Cases ***

# ════════════════════════════════════════════════════════════════
#  БЛОК 1: РЕЄСТРАЦІЯ
# ════════════════════════════════════════════════════════════════

TC-01 Сторінка реєстрації відкривається коректно
    [Tags]    registration    smoke
    Очистити сесію
    Перейти на сторінку реєстрації
    Page Should Contain      Sign Up
    Element Should Be Visible    id=username
    Element Should Be Visible    id=email
    Element Should Be Visible    id=password
    Element Should Be Visible    id=confirm
    Element Should Be Visible    id=register

TC-02 Успішна реєстрація нового користувача
    [Tags]    registration    positive
    Очистити сесію
    Зареєструвати користувача
    ...    ${UNIQUE_USER}
    ...    ${UNIQUE_EMAIL}
    ...    Password1!
    ...    Password1!
    Перевірити успішне повідомлення
    Перевірити що сторінка містить текст    Congrats
    Перевірити що знаходимось на сторінці    ${BASE_URL}/

TC-03 Реєстрація з паролями що не співпадають
    [Tags]    registration    negative
    Очистити сесію
    Зареєструвати користувача
    ...    rf_mismatch
    ...    mismatch@example.com
    ...    Password1!
    ...    DifferentPass!
    Перевірити що знаходимось на сторінці    ${BASE_URL}/auth/register

TC-04 Реєстрація з вже існуючим email
    [Tags]    registration    negative
    Очистити сесію
    Зареєструвати користувача
    ...    rf_another
    ...    ${UNIQUE_EMAIL}
    ...    Password1!
    ...    Password1!
    Перевірити що знаходимось на сторінці    ${BASE_URL}/auth/register

TC-05 Реєстрація з вже існуючим username
    [Tags]    registration    negative
    Очистити сесію
    Зареєструвати користувача
    ...    ${UNIQUE_USER}
    ...    unique_new@example.com
    ...    Password1!
    ...    Password1!
    Перевірити що знаходимось на сторінці    ${BASE_URL}/auth/register

# ════════════════════════════════════════════════════════════════
#  БЛОК 2: ВХІД / ВИХІД
# ════════════════════════════════════════════════════════════════

TC-06 Сторінка входу відкривається коректно
    [Tags]    login    smoke
    Очистити сесію
    Перейти на сторінку входу
    Page Should Contain      Sign In
    Element Should Be Visible    id=username
    Element Should Be Visible    id=password
    Element Should Be Visible    id=login

TC-07 Успішний вхід з валідними даними
    [Tags]    login    positive
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Перевірити успішне повідомлення
    Перевірити що кнопка logout присутня
    Перевірити що знаходимось на сторінці    ${BASE_URL}/

TC-08 Вхід з невірним паролем
    [Tags]    login    negative
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    WrongPassword!
    Перевірити повідомлення про помилку
    Перевірити що знаходимось на сторінці    ${BASE_URL}/auth/login

TC-09 Вхід з неіснуючим користувачем
    [Tags]    login    negative
    Очистити сесію
    Увійти як    nobody_xyz_999    Password1!
    Перевірити повідомлення про помилку
    Перевірити що знаходимось на сторінці    ${BASE_URL}/auth/login

TC-10 Успішний вихід з системи
    [Tags]    login    positive
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Вийти з системи
    Перевірити що знаходимось на сторінці    ${BASE_URL}/
    Перевірити що кнопка logout відсутня

# ════════════════════════════════════════════════════════════════
#  БЛОК 3: СКИДАННЯ ПАРОЛЮ
# ════════════════════════════════════════════════════════════════

TC-11 Сторінка скидання паролю відкривається
    [Tags]    password_reset    smoke
    Очистити сесію
    Перейти на сторінку забули пароль
    Page Should Contain      Forgot Password
    Element Should Be Visible    id=email
    Element Should Be Visible    id=forgot

TC-12 Запит скидання паролю для існуючого email
    [Tags]    password_reset    positive
    Очистити сесію
    Перейти на сторінку забули пароль
    Input Text           id=email    ${UNIQUE_EMAIL}
    Безпечний клік       id=forgot
    Перевірити що URL містить    /auth/login
    Element Should Be Visible    css=.alert

TC-13 Запит скидання паролю для неіснуючого email
    [Tags]    password_reset    negative
    Очистити сесію
    Перейти на сторінку забули пароль
    Input Text           id=email    nobody@nowhere.com
    Безпечний клік       id=forgot
    Перевірити що URL містить    /auth/login
    Element Should Be Visible    css=.alert

# ════════════════════════════════════════════════════════════════
#  БЛОК 4: ПОСТИ
# ════════════════════════════════════════════════════════════════

TC-14 Неавторизований користувач не може створити пост
    [Tags]    posts    negative    auth
    Очистити сесію
    Перейти на сторінку створення поста
    Перевірити що URL містить    /auth/login
    Page Should Contain    Sign In

TC-15 Форма створення поста відображається для авторизованого
    [Tags]    posts    smoke
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Перейти на сторінку створення поста
    Page Should Contain      Add a Blog/Post
    Element Should Be Visible    id=title
    Element Should Be Visible    id=description
    Element Should Be Visible    id=body
    Element Should Be Visible    id=post

TC-16 Успішне створення нового поста
    [Tags]    posts    positive
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Створити пост
    ...    Тестовий пост Robot Framework
    ...    Короткий опис тестового поста
    ...    Детальний текст поста, що створено через Robot Framework Keyword Driven Testing.
    Перевірити успішне повідомлення
    Перевірити що сторінка містить текст    Blog Post posted successfully!
    Перевірити що сторінка містить текст    Тестовий пост Robot Framework

TC-17 Створення поста без заголовку не проходить
    [Tags]    posts    negative
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Перейти на сторінку створення поста
    Input Text           id=description    Опис без заголовку
    Input Text           id=body           Тіло поста без заголовку.
    Безпечний клік       id=post
    Перевірити що знаходимось на сторінці    ${BASE_URL}/posts/create

TC-18 Пости відображаються на головній сторінці
    [Tags]    posts    smoke
    Очистити сесію
    Перейти на головну сторінку
    Element Should Be Visible        id=post_listing
    Перевірити що сторінка містить текст    Тестовий пост Robot Framework

# ════════════════════════════════════════════════════════════════
#  БЛОК 5: КОМЕНТАРІ
# ════════════════════════════════════════════════════════════════

TC-19 Неавторизований не бачить форму коментаря
    [Tags]    comments    negative    auth
    Очистити сесію
    Перейти на головну сторінку
    Click Link    Тестовий пост Robot Framework
    Page Should Not Contain Element    id=add_comment

TC-20 Успішне додавання коментаря до поста
    [Tags]    comments    positive
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Перейти на головну сторінку
    Click Link    Тестовий пост Robot Framework
    Input Text           id=name       Robot Tester
    Input Text           id=message    Коментар від Robot Framework!
    Безпечний клік       id=add_comment
    Перевірити що сторінка містить текст    Comment added to the Post successfully!

# ════════════════════════════════════════════════════════════════
#  БЛОК 6: ПРОФІЛЬ
# ════════════════════════════════════════════════════════════════

TC-21 Неавторизований не має доступу до профілю
    [Tags]    profile    negative    auth
    Очистити сесію
    Go To    ${BASE_URL}/users/settings/profile
    Перевірити що URL містить    /auth/login
    Page Should Contain    Sign In

TC-22 Сторінка профілю відкривається для авторизованого
    [Tags]    profile    smoke
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Перейти на профіль
    Page Should Contain      Your Profile
    Element Should Be Visible    id=firstname
    Element Should Be Visible    id=lastname
    Element Should Be Visible    id=bio
    Element Should Be Visible    id=update_profile

TC-23 Успішне оновлення профілю
    [Tags]    profile    positive
    Очистити сесію
    Увійти як    ${UNIQUE_USER}    Password1!
    Оновити профіль    Robot    Tester    Автоматичний тестувальник Robot Framework
    Перевірити успішне повідомлення
    Перевірити що сторінка містить текст    Profile updated successfully!

TC-24 Публічний профіль користувача доступний
    [Tags]    profile    smoke
    Очистити сесію
    Go To    ${BASE_URL}/users/${UNIQUE_USER}
    Page Should Contain    ${UNIQUE_USER}
    Page Should Contain    Posts
