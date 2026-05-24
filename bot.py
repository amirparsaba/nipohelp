import asyncio
from balethon import Client
from config import BOT_TOKEN, DEBUG
from database import db

from start import register_start_handlers
from categories import register_category_handlers
from requests import register_request_handlers
from admin import register_admin_handlers

bot = Client(token=BOT_TOKEN)

async def main():
    print("=" * 40)
    print("🤖 NipoHelp - راه‌اندازی...")
    
    await db.connect()
    
    register_start_handlers(bot)
    register_category_handlers(bot)
    register_request_handlers(bot)
    register_admin_handlers(bot)
    
    print("✅ ربات آماده است!")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 ربات متوقف شد.")