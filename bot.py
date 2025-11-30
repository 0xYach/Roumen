import os
import json
from mega import Mega
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

# Initialize MEGA
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# Local books storage
BOOKS_FILE = 'books.json'

# --- Telegram Bot Commands ---

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Book Tracker Bot!\n"
        "Use /backup to upload books.json to MEGA.\n"
        "Use /restore <MEGA_LINK> to restore books.json from MEGA."
    )

# /backup command
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = m.upload(BOOKS_FILE)
        link = m.get_upload_link(file)
        await update.message.reply_text(f"Backup complete!\nMEGA link: {link}")
    except Exception as e:
        await update.message.reply_text(f"Backup failed: {str(e)}")

# /restore command
async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide the MEGA file link. Example:\n/restore <MEGA_LINK>")
        return
    mega_file_link = context.args[0]
    try:
        m.download_url(mega_file_link, dest_filename=BOOKS_FILE)
        with open(BOOKS_FILE, 'r') as f:
            books = json.load(f)
        await update.message.reply_text(f"Restore complete! {len(books)} books loaded.")
    except Exception as e:
        await update.message.reply_text(f"Restore failed: {str(e)}")

# --- Main ---

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("backup", backup))
app.add_handler(CommandHandler("restore", restore))

print("Bot is running...")
app.run_polling()
