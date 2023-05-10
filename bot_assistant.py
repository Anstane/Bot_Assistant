import os
import logging

from aiogram import Bot, Dispatcher, executor, types
import aiohttp

from dotenv import load_dotenv

import translators as ts


load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
weather_token = os.getenv('WEATHER_TOKEN')


logging.basicConfig(level=logging.INFO)


bot = Bot(token=telegram_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Ответ на /start."""
    text = 'Здравствуйте! В каком городе вы хотели бы узнать погоду?'
    await message.answer(text)


# Нужно сделать, чтобы это было единственной кнопкой.
# Возможно сделать кнопками самые частые запросы.
# async def get_city_name(update, context):
#     """Ответ на /weather_forecast."""
#     text = 'Please enter the name of a city to get the current weather forecast:'
#     await update.message.reply_text(text)


async def get_weather_forecast(city):
    """Получаем прогноз погоды.
    
    Делаем запрос к API OpenWeatherMap передавая в параметрах название города.
    """
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': weather_token}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=endpoint, params=params) as response:
                weather_json = await response.json()
    except aiohttp.ClientConnectionError as error:
        logging.error(f'Не удаётся установить соединение с API: {error}')
        return 'Что-то пошло не так.'

    try:
        return weather_json
    except KeyError as error:
        logging.error(f'Данные о погоде не были получены: {error}')
        return 'Что-то пошло не так.'


async def translate_city_name(city):
    """Переводим полученное название города с русского на английский."""
    return ts.translate_text(city, translator='google', from_language='ru')


async def translate_weather_forecast(weather):
    """Переводим полученный прогноз погоды с английского на русский."""
    return ts.translate_text(weather, translator='google', to_language='ru')


@dp.message_handler()
async def main(message: types.Message):
    """Реализация основной функции."""
    city_in_eng = await translate_city_name(message.text)
    weather_json = await get_weather_forecast(city_in_eng)
    
    if not weather_json:
        error_message = 'Не удалось получить данные о погоде. Пожалуйста, попробуйте позже.'
        await message.answer(error_message)
    else:
        weather_text = await translate_weather_forecast(weather_json['weather'][0]['description'])
        temp = str(round(weather_json['main']['temp'] - 273.15, 1))
        temp_feels_like = str(round(weather_json['main']['feels_like'] - 273.15, 1))
        text = f'Погода в городе {city_in_eng.capitalize()}:\n{weather_text}, температура: {temp} °C (ощущается как {temp_feels_like} °C).'
        await message.answer(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
