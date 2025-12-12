# YAMail Bot for Telegram

Телеграм-бот, который принимает файлы от пользователей и сохраняет их на их собственные Яндекс.Диски. Бот поддерживает полноценный OAuth-поток с автоматическим callback на FastAPI, так что подключение происходит в одно нажатие.

## Возможности
- `/start` с подсказками.
- `/connect` выдаёт OAuth-ссылку на Яндекс.Диск с передачей Telegram `user_id` через `state`.
- FastAPI-эндпоинт `/oauth/callback` автоматически принимает `code`, обменивает его на `access_token`, сохраняет токен в базе и присылает пользователю уведомление в Telegram.
- Приём документов, фото, видео, голосовых сообщений и стикеров.
- Автоматическое создание папок и загрузка на Диск через публичный API.
- Сообщения о свободном и использованном месте после загрузки.

## Требования
- Зарегистрированное OAuth-приложение Яндекс.Диска.
- Токен Telegram Bot API.

Все зависимости перечислены в `requirements.txt` (`aiogram`, `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `pytest`).

## Настройка Яндекс OAuth
1. Создайте приложение на https://oauth.yandex.ru/client/new.
2. Разрешите доступ к Яндекс.Диску и укажите Redirect URI: `https://<ваш-домен>/oauth/callback` (или домен Timeweb).
3. Сохраните `client_id` и `client_secret` — они понадобятся в `.env`.

## Переменные окружения
Пример находится в `.env.example`.

- `TELEGRAM_TOKEN` — токен бота от @BotFather.
- `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` — данные OAuth-приложения.
- `YANDEX_REDIRECT_URI` — Redirect URI, настроенный в Яндексе (должен совпадать).
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
5. В Яндекс OAuth укажите Redirect URI вашего хоста (например, `http://localhost:8000/oauth/callback` для локальной проверки).

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
2. Создайте OAuth-приложение Яндекс.Диска с Redirect URI вида `https://<ваш-timeweb-домен>/oauth/callback`.
3. В панели Timeweb создайте проект Docker Compose, загрузите `docker-compose.yml` и `.env`.
4. Убедитесь, что порт 8000 проброшен наружу, чтобы Яндекс мог обратиться к `/oauth/callback`.
5. После деплоя отправьте команду `/connect` боту — авторизация пройдёт в одно нажатие, а токены сохранятся в `data/users.db`.

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