from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import db
from keyboards import session_kb

def setup_scheduler(bot):
    sch = AsyncIOScheduler(timezone="UTC")
    sch.add_job(tick, IntervalTrigger(minutes=1), args=[bot], max_instances=1)
    return sch

async def tick(bot):
    for user in await db.all_users():
        now = datetime.now(ZoneInfo(user["tz"]))
        if now.strftime("%H:%M") != user["remind_time"] or user["last_remind"] == now.date().isoformat():
            continue
        await db.set_last_remind(user["chat_id"], now.date().isoformat())
        await bot.send_message(user["chat_id"], "⏰ Время занятия! Выберите режим:",
                               reply_markup=session_kb())