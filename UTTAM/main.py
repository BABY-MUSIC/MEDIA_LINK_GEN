import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Bot token
TOKEN = '7472927630:AAHueShYWJSd-n0rPFZOcjM-lV9W7zcqRrQ'

def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}
    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        return True, response.json().get('url', 'No URL found')
    else:
        return False, f"Error: {response.status_code} - {response.text}"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a media file to upload on Catbox!")

def handle_media(update: Update, context: CallbackContext) -> None:
    media = update.message.reply_to_message
    if not media:
        return update.message.reply_text("Please reply to a media file.")

    file_size = 0
    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size

    if file_size > 200 * 1024 * 1024:
        return update.message.reply_text("Please provide a media file under 200MB.")

    try:
        text = update.message.reply_text("Processing...")

        local_path = media.download()  # Download the file

        text.edit_text("Uploading to Catbox...")
        success, upload_path = upload_file(local_path)

        if success:
            text.edit_text(
                f"Upload successful! [Click here]({upload_path})",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("View File", url=upload_path)]
                ])
            )
        else:
            text.edit_text(f"An error occurred while uploading: {upload_path}")

        os.remove(local_path)  # Clean up local file

    except Exception as e:
        text.edit_text(f"File upload failed: {e}")
        if os.path.exists(local_path):
            os.remove(local_path)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.reply & (Filters.photo | Filters.video | Filters.document), handle_media))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
