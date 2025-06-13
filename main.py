import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiohttp import web
import json
import os

API_TOKEN = "8159576173:AAG6sa6ax2Ude73GEdYvnNR4eFq3dJQQHL4"
CHANNEL_ID = "@luchshe_kazhdy_den"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://telegram-autopost-bot.onrender.com" + WEBHOOK_PATH

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

async def scheduler():
    while True:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        try:
            with open("posts.json", "r", encoding="utf-8") as f:
                posts = json.load(f)
        except Exception as e:
            logging.error(f"Ошибка чтения posts.json: {e}")
            await asyncio.sleep(60)
            continue

        for post in posts[:]:
            if post["datetime"] == now:
                text = post["text"]
                image_path = post.get("image_path")
                try:
                    if image_path and os.path.exists(image_path):
                        with open(image_path, "rb") as photo:
                            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text)
                    else:
                        await bot.send_message(chat_id=CHANNEL_ID, text=text)
                    posts.remove(post)
                    with open("posts.json", "w", encoding="utf-8") as f:
                        json.dump(posts, f, indent=2, ensure_ascii=False)
                    logging.info(f"Опубликовано: {text}")
                except Exception as e:
                    logging.error(f"Ошибка публикации: {e}")

        await asyncio.sleep(60)

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Бот работает по webhook и публикует посты автоматически.")

# --- Webhook конфигурация ---

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    logging.info("Webhook удалён")

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
setup_application(app, dp, bot=bot)
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

loop = asyncio.get_event_loop()
loop.create_task(scheduler())

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=10000)
