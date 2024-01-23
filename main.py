import asyncio
import os


from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from bot.handlers.users_handlers import register_user_handlers

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.scheduler.users_schedulers import register_user_scheduler


def register_handler(dp: Dispatcher) -> None:
    register_user_handlers(dp)


def register_scheduler(scheduler: AsyncIOScheduler) -> None:
    register_user_scheduler(scheduler)


async def main() -> None:
    load_dotenv('.env')
    token = os.getenv('TOKEN_API')
    bot = Bot(token)
    dp = Dispatcher(bot)
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    register_handler(dp)
    register_scheduler(scheduler)

    try:
        scheduler.start()
        await dp.start_polling()
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    asyncio.run(main())
