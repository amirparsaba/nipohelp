from balethon import Client
from balethon.objects import InlineKeyboardButton
from database import db

def register_category_handlers(bot: Client):
    
    @bot.on_callback(lambda c: c.data and c.data.startswith("cat_"))
    async def show_subs(cq):
        cat_id = int(cq.data.split("_")[1])
        subs = await db.get_subcategories(cat_id)
        if not subs:
            await cq.answer("زیرمجموعه‌ای ندارد!", show_alert=True)
            return
        
        keyboard = []
        for s in subs:
            keyboard.append([InlineKeyboardButton(text=f"{s['icon']} {s['name']}", callback_data=f"sub_{s['id']}")])
        keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_menu")])
        
        await cq.answer()
        await cq.message.edit_text("🔍 زیردسته رو انتخاب کن:", reply_markup=keyboard)
    
    @bot.on_callback(lambda c: c.data and c.data.startswith("sub_"))
    async def show_links(cq):
        sub_id = int(cq.data.split("_")[1])
        links = await db.get_links(sub_id)
        if not links:
            await cq.answer("هیچ لینکی نیست!", show_alert=True)
            return
        
        txt = "🔗 **لینک‌های مفید:**\n\n"
        for i, l in enumerate(links, 1):
            txt += f"{i}. **[{l['title']}]({l['url']})**\n"
            if l['description']:
                txt += f"   📝 {l['description']}\n"
            txt += "\n"
        
        keyboard = [
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_menu")],
            [InlineKeyboardButton(text="➕ پیشنهاد لینک", callback_data="new_request")]
        ]
        
        await cq.answer()
        await cq.message.edit_text(txt, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)