import asyncio
from balethon import Client
from balethon.objects import Message
from balethon.objects import InlineKeyboardButton, inline_keyboard_button

bot = Client(token="YOUR_BOT_TOKEN_HERE")  # توکن رو عوض کن

@bot.on_command("start")
async def start_handler(message: Message):
    keyboard = inline_keyboard_button(
        inline_keyboard=[
            [InlineKeyboardButton(text="📁 برنامه‌نویسی", callback_data="cat_1")],
            [InlineKeyboardButton(text="🎨 هنر", callback_data="cat_2")],
            [InlineKeyboardButton(text="➕ پیشنهاد لینک", callback_data="new_request")]
        ]
    )
    await message.reply("🎯 به NipoHelp خوش آمدی!", reply_markup=keyboard)

@bot.on_callback_query()
async def callback_handler(callback):
    await callback.answer()
    data = callback.data
    
    if data == "cat_1":
        keyboard = inline_keyboard_button(
            inline_keyboard=[
                [InlineKeyboardButton(text="🐍 پایتون", callback_data="sub_1")],
                [InlineKeyboardButton(text="📜 جاوااسکریپت", callback_data="sub_2")],
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_menu")]
            ]
        )
        await callback.message.edit_text("🔍 زیردسته رو انتخاب کن:", reply_markup=keyboard)
    
    elif data == "back_menu":
        keyboard = inline_keyboard_button(
            inline_keyboard=[
                [InlineKeyboardButton(text="📁 برنامه‌نویسی", callback_data="cat_1")],
                [InlineKeyboardButton(text="🎨 هنر", callback_data="cat_2")],
                [InlineKeyboardButton(text="➕ پیشنهاد لینک", callback_data="new_request")]
            ]
        )
        await callback.message.edit_text("🎯 منوی اصلی:", reply_markup=keyboard)
    
    elif data == "new_request":
        await callback.message.edit_text("📝 لطفاً نام دسته رو بنویس:\n(مثال: برنامه‌نویسی)\n\nبرای لغو /cancel")

@bot.on_command("cancel")
async def cancel_handler(message: Message):
    await message.reply("❌ لغو شد. /start")

async def main():
    print("🤖 ربات روشن شد!")
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
