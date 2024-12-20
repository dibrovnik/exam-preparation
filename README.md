# Сервис для подготовки к экзаменам

---

Сервис представляет собой монолитное веб-приложение, предназначенное для помощи пользователям в подготовке к экзаменам. Приложение обеспечивает управление учебными материалами, создание тестов, геймификацию процесса обучения и интеграцию с Telegram для взаимодействия и уведомлений.

С помощью сервиса пользователи могут загружать свои вопросы, генерировать тесты, делиться материалами и следить за прогрессом в подготовке.

---

## **Цели проекта**

1. Предоставить удобный инструмент для подготовки к экзаменам.
2. Создать платформу для хранения и управления учебными материалами.
3. Автоматизировать проверку знаний с помощью искусственного интеллекта.
4. Повысить мотивацию пользователей за счет геймификации.
5. Обеспечить удобное взаимодействие через Telegram.

---

## **Ключевые возможности**

1. **Управление материалами**:

    - Загрузка вопросов и ответов из Excel-файлов.
    - Автоматическая обработка и добавление в базу данных.
    - Гибкие настройки доступа к вопросам (личные, публичные, с ограниченным доступом).

2. **Тестирование**:

    - Генерация тестов по выбранным вопросам.
    - Поддержка вопросов с вариантами ответа и со свободным текстом.
    - Проверка текстовых ответов с помощью GigaChat API.

3. **Геймификация**:

    - Система стриков для поддержания ежедневной активности.
    - Достижения и награды за активность.

4. **Уведомления**:

    - Напоминания через Telegram и email.
    - Интеграция с Kafka для отправки уведомлений.

5. **Telegram-бот**:

    - Вывод списка экзаменов и вопросов.
    - Управление тестированием через удобный интерфейс.
    - Загрузка файлов вопросов через бот.

---

## **Технологический стек**

-   **Backend**: Laravel
-   **База данных**: PostgreSQL
-   **Очереди и кэш**: Redis
-   **Обработка Excel**: PhpSpreadsheet
-   **Очереди событий**: RabbitMQ
-   **AI**: GigaChat API
-   **Интеграции**:
    -   Telegram Bot API

---

## **Структура проекта**

1. **Пользовательский функционал**:

    - Регистрация и авторизация.
    - Управление экзаменами и вопросами.
    - Генерация тестов.
    - Геймификация.
    - Уведомления.

2. **Интеграции**:

    - Telegram-бот для взаимодействия.
    - RabbitMQ для событийной архитектуры.
    - GigaChat от Сбера для реализации проверки развернутых ответов на вопрос

3. **Инфраструктура**:

    - Docker для развертывания.
    - Резервное копирование данных (тома для PostgreSQL и Redis).

## REST API с авторизацией

Проект включает полноценное REST API с использованием Laravel Sanctum для авторизации. Все действия с экзаменами защищены аутентификацией, что обеспечивает безопасность данных пользователей.

### Методы API

#### Группа маршрутов для аутентификации
Эти маршруты позволяют пользователям регистрироваться, входить в систему и завершать сеанс.

- **`POST /auth/register`**  
  Регистрация нового пользователя.  
  **Параметры:**  
  - `name`  
  - `email`  
  - `password`  
  - `password_confirmation`

- **`POST /auth/login`**  
  Авторизация пользователя и получение токена доступа.  
  **Параметры:**  
  - `email`  
  - `password`

- **`POST /auth/logout`**  
  Завершение сеанса пользователя (требует аутентификации).

---

#### Группа маршрутов для работы с экзаменами
Маршруты позволяют управлять экзаменами и импортировать вопросы.

- **`GET /exams`**  
  Получение списка доступных экзаменов.  
  (требует аутентификации).

- **`GET /exams/{exam}`**  
  Получение информации о конкретном экзамене.  
  (требует аутентификации).

- **`POST /exams`**  
  Создание нового экзамена.  
  **Параметры:**  
  - `name`  
  - `date`  
  (требует аутентификации).

- **`PUT /exams/{exam}`**  
  Обновление информации об экзамене.  
  **Параметры:**  
  - `name`  
  - `date`  
  (требует аутентификации).

- **`DELETE /exams/{exam}`**  
  Удаление экзамена.  
  (требует аутентификации).

- **`POST /exams/{exam}/import-questions`**  
  Импорт вопросов в экзамен из файла.  
  **Параметры:**  
  - `file` (файл формата `.xlsx`)  
  (требует аутентификации).
