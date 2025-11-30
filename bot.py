import os
import json
from mega import Mega
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

# -----------------------
# Initialize MEGA
# -----------------------
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# -----------------------
# Books JSON file
# -----------------------
BOOKS_FILE = "books.json"

def ensure_books_file():
    """Create books.json if it doesn't exist."""
    if not os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, "w") as f:
            json.dump([], f)

ensure_books_file()

# -----------------------
# /start command
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Book Tracker Bot\n\n"
        "Commands:\n"
        "/backup – Upload books.json to MEGA\n"
        "/restore <MEGA_LINK> – Restore books.json from MEGA"
    )

# -----------------------
# /backup command
# -----------------------
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = m.upload(BOOKS_FILE)
        link = m.get_upload_link(file)
        await update.message.reply_text(f"Backup completed!\n\nMEGA Link:\n{link}")
    except Exception as e:
        await update.message.reply_text(f"Backup failed:\n{str(e)}")

# -----------------------
# /restore command
# -----------------------
async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Send a MEGA link to restore.\nExample:\n/restore https://mega.nz/xxxx"
        )
        return

    mega_link = context.args[0]

    try:
        m.download_url(mega_link, dest_filename=BOOKS_FILE)

        with open(BOOKS_FILE, "r") as f:
            books = json.load(f)

        await update.message.reply_text(
            f"Restore complete! Loaded {len(books)} books."
        )

    except Exception as e:
        await update.message.reply_text(f"Restore failed:\n{str(e)}")

# -----------------------
# MAIN BOT PROGRAM
# -----------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("restore", restore))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
