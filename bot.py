import asyncio
from datetime import datetime, date
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import init_db, add_expense, get_monthly_report
from config import BOT_TOKEN
from db import get_total_for_current_month
from aiogram.filters import Command


router = Router()
scheduler = AsyncIOScheduler()

@router.message(Command("total"))
async def handle_total_command(message: Message):
    total = await get_total_for_current_month(message.from_user.id)
    await message.answer(f"📊 Текущая сумма трат за {date.today().strftime('%B %Y')}: {total}₽")

@router.message()
async def handle_expense(message: Message):
    try:
        amount = int(message.text.strip())
        await add_expense(message.from_user.id, amount)
        await message.reply(f"✅ Добавлено: {amount}₽")
    except ValueError:
        await message.reply("⚠️ Пожалуйста, отправь сумму трат числом, например: 250")

async def send_monthly_report(bot: Bot):
    today = date.today()
    if today.day != 1:
        return

    user_ids = [123456789]  # Позже можно хранить в базе список пользователей
    for user_id in user_ids:
        year, month = today.year, today.month - 1 or (today.year - 1, 12)
        rows = await get_monthly_report(user_id, year, month)
        if not rows:
            continue
        total = sum(row[1] for row in rows)
        breakdown = "\n".join([f"{row[0]} — {row[1]}₽" for row in rows])
        text = f"📅 Отчёт за {month:02d}.{year}:\n\n💰 Всего: {total}₽\n\n{breakdown}"
        await bot.send_message(user_id, text)

async def main():
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Планировщик запускается каждый день в 00:00, но отчёт только если 1-е число
    scheduler.add_job(send_monthly_report, 'cron', hour=0, minute=0, args=[bot])
    scheduler.start()

    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
