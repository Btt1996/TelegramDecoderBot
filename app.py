import os
import base64
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Helper function to detect and decode Base64 strings
def detect_and_decode_base64(file_content):
    decoded_parts = []
    for line in file_content.splitlines():
        for part in line.split():
            try:
                # Validate Base64 content
                decoded = base64.b64decode(part, validate=True).decode('utf-8')
                decoded_parts.append(decoded)
            except Exception:
                pass  # Ignore non-Base64 parts
    return decoded_parts

# Start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me a file, and I'll extract and decode Base64 content for you!")

# File handler
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file_path = f"{file.file_id}"

    # Download the file
    file.download(file_path)

    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()

    # Detect and decode Base64
    decoded_parts = detect_and_decode_base64(content)
    
    if decoded_parts:
        for part in decoded_parts:
            update.message.reply_text(part)
    else:
        update.message.reply_text("No Base64-encoded content found.")

    # Cleanup
    os.remove(file_path)

# Main function to start the bot
def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')  # Use environment variable for security
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # Command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
