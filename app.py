import os
import base64
import plistlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters

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

# Function to process .plist files
def process_plist(file_content):
    try:
        # Parse the plist content (which is usually in XML format)
        plist_data = plistlib.loads(file_content)
        return plist_data
    except Exception as e:
        return f"Error processing plist: {str(e)}"

# Start command handler
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me a file, and I'll extract and decode Base64 content or process plist files for you!")

# File handler
async def handle_file(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file_path = f"{file.file_id}"

    # Get the file extension
    file_extension = os.path.splitext(file_path)[1].lower()

    # Notify the user that the file type is being processed
    await update.message.reply_text(f"The {file_extension[1:].upper()} file is being processed...")

    # Download the file content as a bytearray
    file_content = await file.download_as_bytearray()

    # Handle different file types based on extension
    if file_extension == ".plist":
        # Process plist file
        plist_data = process_plist(file_content)
        await update.message.reply_text(f"Processed plist data: {plist_data}")
    else:
        # Decode the file content if it's not plist (e.g., Base64)
        content = file_content.decode('utf-8', errors='ignore')
        decoded_parts = detect_and_decode_base64(content)

        if decoded_parts:
            for part in decoded_parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text("No Base64-encoded content found.")

# Main function to start the bot
async def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')  # Use environment variable for security
    application = Application.builder().token(TOKEN).build()

    # Command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
