#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import re
import requests
import openai
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === Переменные окружения ===
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Flask-приложение ===
app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# === GPT-функция ===
def ask_gpt(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Или gpt-3.5-turbo, если экономить
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"]

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли ссылку на Wildberries или опиши, что ищешь 🛍")

# === Обработка сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "wildberries.ru/catalog/" in text:
        match = re.search(r'catalog/(\d+)/', text)
        if not match:
            await update.message.reply_text("❗ Не удалось извлечь ID товара.")
            return

        product_id = match.group(1)
        try:
            url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={product_id}"
            response = requests.get(url).json()
            product = response["data"]["products"][0]
            title = product["name"]
            price = product["salePriceU"] // 100

            await update.message.reply_text(f"🛒 {title}\n💰 Цена: {price} ₽")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка: {e}")
    else:
        gpt_response = ask_gpt(f"Пользователь написал: '{text}'. Что он хочет найти на Wildberries?")
        await update.message.reply_text(f"🤖 GPT думает:\n{gpt_response}")

# === Добавление хендлеров ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Webhook для Telegram ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# === Healthcheck (Render проверяет, жив ли сервис) ===
@app.route("/", methods=["GET"])
def health():
    return "Бот жив!"

# === Запуск Flask-сервера ===
if __name__ == "__main__":
    print("⚙️ Запуск Flask-сервера")

    port = os.environ.get("PORT")
    if not port or port == "":
        port = 5000
    else:
        port = int(port)

    app.run(host="0.0.0.0", port=port)




# In[ ]:




