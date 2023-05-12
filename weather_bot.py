import os
import logging

from aiogram import (Bot, Dispatcher, executor, types)
import aiohttp

from exceptions import (APIAnswerIsEmptyException, 
                        ProgramErrorException)

from dotenv import load_dotenv


load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
weather_token = os.getenv('WEATHER_TOKEN')
traslator_token = os.getenv('IAM_TOKEN')
folder_id = os.getenv('folderId')


logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s'
)


bot = Bot(token=telegram_token)
dp = Dispatcher(bot)


app_storage = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Ответ на /start."""
    kb = [
        [
            types.KeyboardButton(text='Москва'),
            types.KeyboardButton(text='Екатеринбург'),
            types.KeyboardButton(text='Иркутск'),
            types.KeyboardButton(text='Нижний Тагил')
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    text = 'Здравствуйте! В каком городе вы хотели бы узнать погоду?'
    await message.answer(text, reply_markup=keyboard)
    logging.info('Обработана команда /start.')


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    """Ответ на /help."""
    text = 'Для получения прогноза погоды - напишите название интересующего Вас города.'
    await message.answer(text)
    logging.info('Обработана команда /help.')


async def get_weather_forecast(city):
    """Получаем прогноз погоды.
    
    Делаем запрос к API OpenWeatherMap передавая в параметрах название города.
    """
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': weather_token}

    try:
        async with app_storage['session'].get(url=endpoint, params=params) as response:
            weather_json = await response.json()

    except aiohttp.ClientConnectionError as error:
        logging.error(f'Не удаётся установить соединение с API: {error}.')
        raise error

    try:
        return weather_json

    except APIAnswerIsEmptyException as error:
        logging.error(f'Данные о погоде не были получены: {error}.')
        raise error


async def translator(text, target_language):
    """Интегрируем Яндекс Переводчик.
    
    Обращаемся к API Яндекс Переводчика передавая текст и желаемый язык для перевода.
    """
    endpoint = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    body = {
        "targetLanguageCode": target_language,
        "texts": text,
        "folderId": folder_id,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(traslator_token)
    }

    try:
        async with app_storage['session'].post(url=endpoint, json=body, headers=headers) as response:
            translated_json = await response.json()

    except aiohttp.ClientConnectionError as error:
        logging.error(f'Не удаётся установить соединение с API: {error}.')
        raise error

    try:
        return translated_json['translations'][0]['text']

    except APIAnswerIsEmptyException as error:
        logging.error(f'Ответ переводчика оказался пустым: {error}.')
        raise error


@dp.message_handler()
async def main(message: types.Message):
    """Реализация основной функции."""

    app_storage['session'] = aiohttp.ClientSession()

    try:
        city = await translator(message.text, 'en')
        weather_json = await get_weather_forecast(city)

        weather = weather_json['weather'][0]['description']
        translated_weather = await translator(weather, 'ru')

        temp = round(weather_json['main']['temp'] - 273.15, 1)
        temp_feels_like = round(weather_json['main']['feels_like'] - 273.15, 1)

        text = (
            f'Погода в городе {message.text.capitalize()}:\n'
            f'{translated_weather.capitalize()}, '
            f'температура: {temp} °C '
            f'(ощущается как {temp_feels_like} °C).'
        )
        await message.answer(text)
        logging.info(f'Было отправлено сообщение: {text}')

    except ProgramErrorException as error:
        await message.answer('В работе программы возникла проблема.')
        logging.error(f'Возникла ошибка: {error}')


if __name__ == '__main__':
    print('Бот начал работу.')
    executor.start_polling(dp, skip_updates=True)
    print('Бот прекратил свою работу.')
