#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("7796351663:AAFzbqu8O5kl36mTtk8FQuzemtaX6PNdNPI")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли ссылку на Wildberries — я скажу цену 🛍")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "wildberries.ru/catalog/" in text:
        try:
            match = re.search(r'catalog/(\d+)/', text)
            if not match:
                await update.message.reply_text("❗ Не удалось извлечь ID товара.")
                return

            product_id = match.group(1)
            api_url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&nm={product_id}"
            response = requests.get(api_url).json()
            product = response["data"]["products"][0]
            title = product["name"]
            price = product["salePriceU"] // 100

            await update.message.reply_text(f"🛒 {title}\n💰 Цена: {price} ₽")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка: {e}")
    else:
        await update.message.reply_text("Понимаю только ссылки на Wildberries 😉")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    app.run_polling()


# In[ ]:




