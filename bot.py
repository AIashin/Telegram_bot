#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import requests
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import Dispatcher

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()
dispatcher = application.dispatcher

# --- GPT функция
def ask_gpt(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Или gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"]

# --- Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли ссылку на Wildberries или опиши, что ищешь 👀")

# --- Обработка текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "wildberries.ru/catalog/" in text:
        match = re.search(r'catalog/(\d+)/', text)
        if not match:
            await update.message.reply_text("❗ Не удалось извлечь ID товара.")
            return

        product_id = match.group(1)
        try:
            api_url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={product_id}"
            response = requests.get(api_url).json()
            product = response["data"]["products"][0]
            title = product["name"]
            price = product["salePriceU"] // 100
            await update.message.reply_text(f"🛒 {title}\n💰 Цена: {price} ₽")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка: {e}")
    else:
        gpt_response = ask_gpt(f"Пользователь ищет на Wildberries: {text}. Помоги интерпретировать запрос и дай совет.")
        await update.message.reply_text(f"🤖 {gpt_response}")

# --- Хендлеры
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask endpoint для Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# --- Healthcheck
@app.route("/")
def home():
    return "Бот жив!"

# --- Запуск
if __name__ == "__main__":
    print("⚙️ Запуск Flask-сервера")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


# In[ ]:




