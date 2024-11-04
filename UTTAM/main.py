import logging
import requests
import json
import sys
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set the path to the parent directory to import config.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config  # Now this will import the config from the parent directory

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a photo or video, and I will upload it to ImgBB.')

def upload_to_imgbb(file_url: str) -> str:
    response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={
            'key': config.IMGBB_API_KEY,
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

def main() -> None:
    updater = Updater(config.TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
