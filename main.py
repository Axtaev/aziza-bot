import os
import openai
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Настройки
openai.api_key = os.getenv("OPENAI_API_KEY")
admin_id = int(os.getenv("TELEGRAM_ADMIN_ID"))
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# Логгер
def log_message(user, user_message, bot_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = (
        f"\n[{timestamp}] ✉️ От: {user}\n"
        f"📥 Сообщение: {user_message}\n"
        f"🤖 Ответ: {bot_response}\n"
    )
    print(log_text)
    with open("logs.txt", "a", encoding="utf-8") as file:
        file.write(log_text)
    try:
        bot.send_message(chat_id=admin_id, text=log_text)
    except Exception as e:
        print(f"❌ Не удалось отправить лог админу: {e}")

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Aziza – твой GPT-помощник. Пиши что хочешь 💬")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    username = update.message.from_user.username or update.message.from_user.full_name

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_response = response["choices"][0]["message"]["content"]
    except Exception as e:
        bot_response = f"Ошибка: {e}"

    await update.message.reply_text(bot_response)
    log_message(username, user_message, bot_response)

# Запуск
app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
