import logging
import requests
import json
import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
IMGBB_API_KEY = 'YOUR_IMGBB_API_KEY'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask is running!"

@app.route('/start')
def start_command():
    return "Send a message to the Telegram bot to start!"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a photo or video, and I will upload it to ImgBB.')

def upload_to_imgbb(file_url: str) -> str:
    response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': IMGBB_API_KEY,
            'image': file_url
        }
    )
    data = json.loads(response.text)
    if data['success']:
        return data['data']['url']
    else:
        return 'Error uploading image'

def handle_media(update: Update, context: CallbackContext) -> None:
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        file_url = file.file_path
        imgbb_url = upload_to_imgbb(file_url)
        update.message.reply_text(f'Here is your link: {imgbb_url}')
    
    elif update.message.video:
        file = update.message.video.get_file()
        file_url = file.file_path
        imgbb_url = upload_to_imgbb(file_url)
        update.message.reply_text(f'Here is your link: {imgbb_url}')

async def start_bot() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(start_bot())
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
