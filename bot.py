import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from keep_alive import keep_alive

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "mistralai/mistral-7b-instruct:free"

user_memory = {}

# ===== AI FUNCTION =====
def ask_ai(user_id, message):
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": message})

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": user_memory[user_id][-10:]
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        reply = data["choices"][0]["message"]["content"]

        user_memory[user_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        return str(e)

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is live!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    reply = ask_ai(user_id, text)

    await update.message.reply_text(reply)

# ===== MAIN (IMPORTANT FIX) =====
def main():
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
