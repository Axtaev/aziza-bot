import os
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Клиент OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Telegram токены и ID
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
admin_id = int(os.getenv("TELEGRAM_ADMIN_ID"))

# Асинхронный лог
async def log_message(user, user_message, bot_response):
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
        await bot.send_message(chat_id=admin_id, text=log_text)
    except Exception as e:
        print(f"❌ Не удалось отправить лог админу: {e}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Aziza – твой GPT-помощник. Пиши что хочешь 💬")

# Обработка текста
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    username = update.message.from_user.username or update.message.from_user.full_name

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        bot_response = f"Ошибка: {e}"

    await update.message.reply_text(bot_response)
    await log_message(username, user_message, bot_response)

# Бот-движок
app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
