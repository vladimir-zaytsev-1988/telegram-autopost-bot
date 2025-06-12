import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import InputFile
from config import BOT_TOKEN, CHANNEL_ID
import json
import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def send_scheduled_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for post in posts:
        if post["datetime"] == now:
            photo = InputFile(f"bot/{post['image_path']}")
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=post["text"])

async def scheduler():
    while True:
        await send_scheduled_posts()
        await asyncio.sleep(60)

if __name__ == "__main__":
    from aiogram import executor
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
