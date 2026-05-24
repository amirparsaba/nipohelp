import re
from balethon import Client
from database import db
from config import ADMIN_ID, MAX_DESCRIPTION_LEN

user_states = {}
STEP_CAT, STEP_SUB, STEP_LINK, STEP_DESC = 1, 2, 3, 4

def register_request_handlers(bot: Client):
    
    @bot.on_callback("new_request")
    async def start_request(cq):
        user_states[cq.from_user.id] = {'step': STEP_CAT, 'data': {}}
        await cq.answer()
        await cq.message.edit_text(
            "📝 **مرحله 1 از 4**\nدسته اصلی رو بنویس:\nمثال: برنامه‌نویسی، هنر، ویدیو\n\n❌ لغو: /cancel"
        )
    
    @bot.on_command("cancel")
    async def cancel_req(msg):
        uid = msg.from_user.id
        if uid in user_states:
            del user_states[uid]
            await msg.reply("❌ لغو شد.\nبرای شروع /start")
        else:
            await msg.reply("درخواستی در جریان نیست.")
    
    @bot.on_message()
    async def handle_steps(msg):
        uid = msg.from_user.id
        if uid not in user_states:
            return
        
        state = user_states[uid]
        step = state['step']
        data = state['data']
        text = msg.text.strip()
        
        if step == STEP_CAT:
            if len(text) < 2 or len(text) > 50:
                await msg.reply("نام دسته باید 2 تا 50 کاراکتر باشد. دوباره:")
                return
            data['cat'] = text
            state['step'] = STEP_SUB
            await msg.reply(f"✅ دسته {text}\n\nمرحله 2 از 4\nزیردسته رو بنویس:")
        
        elif step == STEP_SUB:
            if len(text) < 2 or len(text) > 50:
                await msg.reply("نام زیردسته باید 2 تا 50 کاراکتر باشد. دوباره:")
                return
            data['sub'] = text
            state['step'] = STEP_LINK
            await msg.reply(f"✅ زیردسته {text}\n\nمرحله 3 از 4\nلینک رو بنویس (با http:// یا https://):")
        
        elif step == STEP_LINK:
            if not (text.startswith('http://') or text.startswith('https://')):
                await msg.reply("لینک باید با http:// یا https:// شروع بشه. دوباره:")
                return
            data['link'] = text
            state['step'] = STEP_DESC
            await msg.reply(f"✅ لینک ثبت شد.\n\nمرحله 4 از 4\nتوضیحات (حداکثر {MAX_DESCRIPTION_LEN} کاراکتر):")
        
        elif step == STEP_DESC:
            desc = text[:MAX_DESCRIPTION_LEN]
            u = msg.from_user
            rid = await db.save_request(
                u.id, u.username or "", u.first_name or "", u.last_name or "",
                data['cat'], data['sub'], data['link'], desc
            )
            
            admin_txt = (
                f"📥 **درخواست جدید** #{rid}\n"
                f"👤 {u.id} | @{u.username or 'ندارد'}\n"
                f"📂 {data['cat']} › {data['sub']}\n"
                f"🔗 {data['link']}\n"
                f"📝 {desc}\n\n"
                f"✅ /approve ❌ /reject\n(روی همین پیام ریپلای کن)"
            )
            admin_msg = await bot.send_message(ADMIN_ID, admin_txt, parse_mode="Markdown")
            await db.update_request_msg_id(rid, admin_msg.id)
            await msg.reply("✅ درخواستت ثبت شد! در صورت تایید، لینک اضافه میشه.\n/start")
            del user_states[uid]