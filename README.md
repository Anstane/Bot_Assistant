# telegram_bot_assistant

Задачей этого проекта является практика асинхронного программирования.
Я пытаюсь реализовать телеграм бота с использованием библиотеки aiogram для упрощения простых бытовых задач.

Основной фреймворк - aiohttp.
Использованные библиотеки: aiogram, aiologger, python-dotenv.

## Масштабирование проекта

В текущий момент я хотел бы реализовать возможность записывать свои расходы и доходы, создав тем самым менеджер финансов.
Будет добавлена база данных SQLite, в которой будет записана информация по расходам, рассортированная по категориям.

## Установка бота

#### Клонируем репозиторий:

```
  git@github.com:Anstane/bot_assistant.git
```

#### Создаём виртуальное окружение:

```
  python3 -m venv venv
```

#### Устанавливаем requirements.txt:

```
  pip install -r requirements.txt
```

## Список использованных API:

```
  OpenWeatherMap API
  Yandex Translator API
```

Если вы хотите использовать этого бота, вам нужно получить следующие **токены**:

- [OpenWeatherMapToken](https://openweathermap.org/api) - **Current Weather Data**
- [YandexTranslatorToken](https://yandex.ru/dev/translate/) - **IAM-token**
## Автор

- [@Anstane](https://github.com/Anstane)

