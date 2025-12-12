# YAMail Bot for Telegram

Телеграм-бот, который принимает файлы от пользователей и сохраняет их на их собственные Яндекс.Диски. Подключение происходит вручную через verification_code — бот покажет ссылку, пользователь авторизуется на странице Яндекса, копирует код и отправляет его боту.

## Возможности
- `/start` с подсказками.
- `/connect` выдаёт OAuth-ссылку на Яндекс.Диск с передачей Telegram `user_id` через `state`.
- Пользователь вручную вводит verification_code из Яндекс OAuth, бот обменивает его на `access_token` и сохраняет токен в базе.
- Приём документов, фото, видео, голосовых сообщений и стикеров.
- Автоматическое создание папок и загрузка на Диск через публичный API.
- Сообщения о свободном и использованном месте после загрузки.

## Требования
- Зарегистрированное OAuth-приложение Яндекс.Диска.
- Токен Telegram Bot API.

Все зависимости перечислены в `requirements.txt` (`aiogram`, `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `pytest`).

## Настройка Яндекс OAuth
1. Создайте приложение на https://oauth.yandex.ru/client/new.
2. Разрешите доступ к Яндекс.Диску (Redirect URI указывать не нужно — Яндекс будет выдавать verification_code по адресу `https://oauth.yandex.ru/verification_code`).
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
5. После запуска отправьте `/connect` боту: он выдаст ссылку на oauth.yandex.ru, скопируйте verification_code со страницы и пришлите его боту.

## Запуск через Docker
1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Соберите образ и поднимите сервис:
   ```bash
   docker compose up --build -d
   ```
3. Бот стартует вместе с FastAPI (порт 8000 по умолчанию). База хранится в `./data/users.db`, примонтированной в контейнер.

## Деплой на Timeweb
Timeweb Cloud поддерживает развёртывание Docker/Compose.

1. Подготовьте `docker-compose.yml` из репозитория и `.env` с продакшен-значениями.
2. Создайте OAuth-приложение Яндекс.Диска. Redirect URI не нужен — используйте стандартный вывод `verification_code`.
3. В панели Timeweb создайте проект Docker Compose, загрузите `docker-compose.yml` и `.env`.
4. После деплоя отправьте команду `/connect` боту — Яндекс покажет verification_code, который нужно переслать боту. Токены сохранятся в `data/users.db`.

## Структура проекта
- `bot/main.py` — запуск aiogram + FastAPI (uvicorn) в одном процессе.
- `bot/handlers.py` — обработчики Telegram-команд и загрузок.
- `web/server.py` — FastAPI-приложение с OAuth callback.
- `bot/db.py` — слой работы с SQLite (хранение токенов пользователей).
- `bot/yandex_client.py` — работа с API Яндекс.Диска.
- `bot/utils.py` — вспомогательные функции (включая `fibonacci`).
- `tests/` — модульные тесты.

## Тестирование
```bash
pytest
```
Тесты покрывают вспомогательные функции и проверяют, что проект устанавливается корректно.