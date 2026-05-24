import re
from balethon import Client
from database import db
from config import ADMIN_ID

def extract_req_id(text):
    match = re.search(r'#(\d+)', text)
    return int(match.group(1)) if match else None

def register_admin_handlers(bot: Client):
    
    @bot.on_command("approve")
    async def approve_admin(msg):
        if msg.from_user.id != ADMIN_ID:
            return await msg.reply("⛔ دسترسی ندارید.")
        if not msg.reply_to_message:
            return await msg.reply("❌ روی درخواست ریپلای کن و بعد /approve بنویس.")
        
        rid = extract_req_id(msg.reply_to_message.text or "")
        if not rid:
            return await msg.reply("❌ شماره درخواست پیدا نشد.")
        
        note = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else "تایید شد"
        ok = await db.approve_request(rid, note)
        if ok:
            req = await db.get_request(rid)
            await msg.reply(f"✅ درخواست #{rid} تایید شد.")
            if req and req['user_id']:
                try:
                    await bot.send_message(req['user_id'], f"✅ درخواست لینک شما تایید شد!\nدسته {req['category_name']} › {req['subcategory_name']}")
                except:
                    pass
        else:
            await msg.reply(f"❌ درخواست #{rid} پیدا نشد.")
    
    @bot.on_command("reject")
    async def reject_admin(msg):
        if msg.from_user.id != ADMIN_ID:
            return await msg.reply("⛔ دسترسی ندارید.")
        if not msg.reply_to_message:
            return await msg.reply("❌ روی درخواست ریپلای کن و بعد /reject بنویس.")
        
        rid = extract_req_id(msg.reply_to_message.text or "")
        if not rid:
            return await msg.reply("❌ شماره درخواست پیدا نشد.")
        
        note = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else "رد شد"
        ok = await db.reject_request(rid, note)
        if ok:
            req = await db.get_request(rid)
            await msg.reply(f"✅ درخواست #{rid} رد شد.")
            if req and req['user_id']:
                try:
                    await bot.send_message(req['user_id'], f"❌ درخواست لینک شما رد شد.\nدلیل: {note}")
                except:
                    pass
        else:
            await msg.reply(f"❌ درخواست #{rid} پیدا نشد.")
    
    @bot.on_command("pending")
    async def pending_list(msg):
        if msg.from_user.id != ADMIN_ID:
            return
        pendings = await db.get_pending_requests()
        if not pendings:
            return await msg.reply("📭 درخواست pending ای نیست.")
        txt = "📋 لیست درخواست‌های pending:\n\n"
        for r in pendings:
            txt += f"🆔 #{r['id']} | {r['category_name']} › {r['subcategory_name']}\n👤 {r['user_id']}\n🔗 {r['link'][:50]}...\n{'-'*30}\n"
        await msg.reply(txt)
    
    @bot.on_command("stats")
    async def stats_admin(msg):
        if msg.from_user.id != ADMIN_ID:
            return
        async with db.pool.acquire() as conn:
            pending = await conn.fetchval("SELECT COUNT(*) FROM requests WHERE status='pending'")
            links = await conn.fetchval("SELECT COUNT(*) FROM links")
        await msg.reply(f"📊 آمار:\n⏳ pending: {pending}\n🔗 لینک‌ها: {links}")
    
    @bot.on_command("helpadmin")
    async def admin_help(msg):
        if msg.from_user.id != ADMIN_ID:
            return
        await msg.reply(
            "🔧 **راهنما:**\n"
            "• /pending - لیست درخواست‌ها\n"
            "• /approve - تایید (با ریپلای)\n"
            "• /reject - رد (با ریپلای)\n"
            "• /stats - آمار\n"
            "• /helpadmin - این پیام"
        )