import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = 7258495769

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Access denied.")
        return

    await update.message.reply_text(
        "🎬 AI Director ишга тайёр!\n\n"
        "Мавзуни юборинг."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Access denied.")
        return

    topic = update.message.text

    await update.message.reply_text(
        f"✅ Мавзу қабул қилинди:\n\n{topic}\n\n"
        "🤖 AI Director ишлаяпти..."
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("AI Director Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
