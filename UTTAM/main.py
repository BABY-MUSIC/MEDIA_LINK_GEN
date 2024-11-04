import logging
import requests
import json
import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Set your API keys directly here
TELEGRAM_BOT_TOKEN = '7472927630:AAHueShYWJSd-n0rPFZOcjM-lV9W7zcqRrQ'
IMGBB_API_KEY = '0d6d275cbd8e8b82ce278e742667d40c'

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Flask is running!"

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
        return data['data']['url']  # Return the image link
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

# Run the Flask app and Telegram bot
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    
    # Run the Flask app on the port defined by Heroku
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if not set
    app.run(host='0.0.0.0', port=port)
