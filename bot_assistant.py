import os

from aiohttp import ClientSession

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from dotenv import load_dotenv

import translators as ts


load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
weather_token = os.getenv('WEATHER_TOKEN')


bot = ApplicationBuilder().token(telegram_token).build()
client_session = {}


async def start(update, context):
    """Ответ на /start."""
    text = 'Hello, great to see you! Have a nice day!'
    await update.message.reply_text(text)


# Нужно сделать, чтобы это было единственной кнопкой.
# Возможно сделать кнопками самые частые запросы.
async def get_city_name(update, context):
    """Ответ на /weather_forecast."""
    text = 'Please enter the name of a city to get the current weather forecast:'
    await update.message.reply_text(text)


# Нужно будет обработать вариант, когда города не существует.
async def get_weather_forecast(city):
    """Получаем JSON с погодой и возвращаем его."""
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': weather_token}

    client_session['session'] = ClientSession()

    async with client_session['session'].get(url=endpoint, params=params) as response:
        weather_json = await response.json()

    try:
        return weather_json['weather'][0]['main']
    except KeyError: # Переделать на корректные try/except + добавить логгировние.
        return 'Data is empty.'


# async def formating_weather_forecast(weather):
#     """Преобразуем итоговый результат."""
#     weather_forecast = []
#     temperature = round(weather['main']['temp'] - 273.15, 1)
#     weather_forecast.append(temperature)

#     return weather_forecast


async def translate_city_name(city):
    return ts.translate_text(city, translator='google', from_language='ru')


async def translate_weather_forecast(weather):
    """Переводчик."""
    return ts.translate_text(weather, translator='google', to_language='ru')


async def main(update, context):
    """Реализация основной функции."""
    traslated_city = await translate_city_name(update.message.text)
    weather_json = await get_weather_forecast(traslated_city)
    weather = await translate_weather_forecast(weather_json)
    await update.message.reply_text(weather)


bot.add_handler(CommandHandler('start', start))
bot.add_handler(CommandHandler('weather_forecast', get_city_name))
bot.add_handler(MessageHandler(filters.TEXT, main))


if __name__ == '__main__':
    bot.run_polling()
