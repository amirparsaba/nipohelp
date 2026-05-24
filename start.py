from balethon import Client
from balethon.objects import KeyboardButton, InlineKeyboardButton
from database import db

def register_start_handlers(bot: Client):
    
    @bot.on_command("start")
    async def start_handler(message):
        cats = await db.get_categories()
        keyboard = []
        for c in cats:
            keyboard.append([InlineKeyboardButton(text=f"{c['icon']} {c['name']}", callback_data=f"cat_{c['id']}")])
        keyboard.append([InlineKeyboardButton(text="➕ پیشنهاد لینک جدید", callback_data="new_request")])
        
        await message.reply(
            "🎯 **به NipoHelp خوش آمدی!**\nیک دسته رو انتخاب کن:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    @bot.on_callback("back_menu")
    async def back_menu(cq):
        cats = await db.get_categories()
        keyboard = []
        for c in cats:
            keyboard.append([InlineKeyboardButton(text=f"{c['icon']} {c['name']}", callback_data=f"cat_{c['id']}")])
        keyboard.append([InlineKeyboardButton(text="➕ پیشنهاد لینک جدید", callback_data="new_request")])
        
        await cq.answer()
        await cq.message.edit_text("📂 منوی اصلی:", reply_markup=keyboard)
