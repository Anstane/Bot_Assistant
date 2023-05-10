import os

from dotenv import load_dotenv

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler, 
    MessageHandler, 
    filters
)
import openai


load_dotenv()
tg_token = os.getenv('TELEGRAM_TOKEN')
gpt_token = os.getenv('OPENAI_TOKEN')


openai.api_key = gpt_token
bot = ApplicationBuilder().token(tg_token).build()


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


bot.add_handler(CommandHandler('start', start_com))
bot.add_handler(MessageHandler(filters.ALL, gpt_bot))


if __name__ == '__main__':
    print('Bot started.')
    bot.run_polling()
