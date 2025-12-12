# YAMail Bot for Telegram

Телеграм-бот, который принимает файлы от пользователей и сохраняет их на их собственные Яндекс.Диски. Подключение происходит вручную через `verification_code`: бот покажет ссылку, пользователь авторизуется на странице Яндекса, копирует код и отправляет его боту.

## Возможности
- `/start` с подсказками.
- `/connect` выдаёт OAuth-ссылку на Яндекс.Диск с передачей Telegram `user_id` через `state`.
- Пользователь вручную вводит `verification_code` из Яндекс OAuth, бот обменивает его на `access_token` и сохраняет токен в базе.
- Приём документов, фото, видео, голосовых сообщений и стикеров.
- Автоматическое создание папок и загрузка на Диск через публичный API.
- Сообщения о свободном и использованном месте после загрузки.

## Требования
- Зарегистрированное OAuth-приложение Яндекс.Диска.
- Токен Telegram Bot API.

Все зависимости перечислены в `requirements.txt` (`aiogram`, `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `pytest`).

## Настройка Яндекс OAuth
1. Создайте приложение на https://oauth.yandex.ru/client/new.
2. Разрешите доступ к Яндекс.Диску (Redirect URI указывать не нужно — Яндекс будет выдавать `verification_code` по адресу `https://oauth.yandex.ru/verification_code`).
3. Сохраните `client_id` и `client_secret` — они понадобятся в `.env`.

## Переменные окружения
Пример находится в `.env.example`.

- `TELEGRAM_TOKEN` — токен бота от @BotFather.
- `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` — данные OAuth-приложения.
- `PUBLIC_APP_HOST` — публичная ссылка на бота (например, `https://t.me/your_bot`).
- `API_HOST`, `API_PORT` — хост и порт FastAPI-приложения (по умолчанию `0.0.0.0:8000`).
- `DATABASE_PATH` — путь к файлу SQLite (по умолчанию `data/users.db`).

## Быстрый старт (локально)
1. Склонируйте репозиторий и создайте виртуальное окружение.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте `.env` на основе `.env.example` и заполните значения.
4. Запустите бота и FastAPI:
   ```bash
   python -m bot.main
   ```
5. После запуска отправьте `/connect` боту: он выдаст ссылку на oauth.yandex.ru, скопируйте `verification_code` со страницы и пришлите его боту.

## Запуск через Docker
1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Соберите образ и поднимите сервис:
   ```bash
   docker compose up --build -d
   ```
3. Бот стартует вместе с FastAPI (порт 8000 по умолчанию). База хранится в `./data/users.db`, примонтированной в контейнер.

## Деплой на Timeweb Cloud
Timeweb Cloud поддерживает развёртывание Docker/Compose. Готовый `docker-compose.yml` и `Dockerfile` находятся в корне репозитория.

1. Подготовьте `.env` с продакшен-значениями (`TELEGRAM_TOKEN`, `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET`, `PUBLIC_APP_HOST`).
2. Загрузите в Timeweb файлы `Dockerfile`, `docker-compose.yml`, `requirements.txt` и весь каталог с кодом или укажите репозиторий.
3. В настройках проекта выберите развёртывание по Docker Compose и используйте корневой `docker-compose.yml`. Порт по умолчанию — `8000`.
4. Хранилище SQLite будет создано автоматически в томе `./data`; при необходимости прокиньте постоянный том в интерфейсе Timeweb.
5. После запуска можно проверять состояние контейнера через healthcheck (`/health`), а затем отправить `/connect` боту, чтобы завершить OAuth.

## Структура проекта
- `bot/main.py` — запуск aiogram + FastAPI (uvicorn) в одном процессе.
- `bot/handlers.py` — обработчики Telegram-команд и загрузок.
- `web/server.py` — FastAPI-приложение с OAuth callback и healthcheck.
- `bot/db.py` — слой работы с SQLite (хранение токенов пользователей).
- `bot/yandex_client.py` — работа с API Яндекс.Диска.
- `bot/utils.py` — вспомогательные функции (включая `fibonacci`).
- `tests/` — модульные тесты.

## Тестирование
```bash
pytest
```
Тесты покрывают вспомогательные функции и проверяют, что проект устанавливается корректно.