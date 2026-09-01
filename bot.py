import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, PORT
from database import init_db
from handlers.start import router as start_router
from handlers.registration import router as registration_router
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from handlers.broadcast import router as broadcast_router

routers = [start_router, registration_router, user_router, admin_router, broadcast_router]

# বট ও ডিসপ্যাচার
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# সব রাউটার যুক্ত করুন
for router in routers:
    dp.include_router(router)

# Render-এর জন্য হেলথ চেক সার্ভার
async def health_check(request):
    return web.Response(text="USDT Repay Bot is running")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"Health check server running on port {PORT}")

async def main():
    init_db()  # ডাটাবেস টেবিল তৈরি
    await asyncio.gather(
        dp.start_polling(bot),
        run_web_server()
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
