import os
import requests

from aiohttp import ClientSession

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler, 
    MessageHandler, 
    filters
)
from dotenv import load_dotenv
import openai


load_dotenv()
tg_token = os.getenv('TELEGRAM_TOKEN')
gpt_token = os.getenv('OPENAI_TOKEN')
weather_token = os.getenv('WEATHER_TOKEN')


openai.api_key = gpt_token
bot = ApplicationBuilder().token(tg_token).build()

client_session = {}


async def start_com(update, context):
    text = 'Hello, great to see you! I`m your local GPT-bot.'
    await update.message.reply_text(text)


async def gpt_bot(update, context):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = update.message.text,
        max_tokens = 2048,
        temperature = 0.2
    )
    await update.message.reply_text(response.choices[0].text)


async def get_city_name(update, context):
    await update.message.reply_text('Please enter the name of a city to get the current weather forecast:')


async def get_weather_forecast(city):
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': weather_token}

    client_session['session'] = ClientSession()

    async with client_session['session'].get(url=endpoint, params=params) as response:
        weather_json = await response.json()

    return weather_json


async def weather_forecast(update, context):
    city = update.message.text
    weather_forecast = await get_weather_forecast(city)
    await update.message.reply_text(weather_forecast)

bot.add_handler(CommandHandler('start', start_com))
bot.add_handler(CommandHandler('weather_forecast', get_city_name))
bot.add_handler(MessageHandler(filters.ALL, weather_forecast))
bot.add_handler(MessageHandler(filters.ALL, gpt_bot))


if __name__ == '__main__':
    print('Bot started.')
    bot.run_polling()
