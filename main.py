# Импортируем необходимые библиотеки
import asyncio
import os


from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# импортируем функцию, регистрирующую обработчики команд и сообщений
from bot.handlers.users_handlers import register_user_router
# импортируем функцию, регистрирующую очереди повторяющихся функций
from bot.scheduler.users_schedulers import register_user_scheduler


# функция регестрации обработчиков
def register_router() -> Router:
    return register_user_router()


# функция регестрации очереди повторяющихся функций
def register_scheduler(scheduler: AsyncIOScheduler) -> None:
    register_user_scheduler(scheduler)


# главная функция проекта, в которой происходит
# конфигурация бота

async def main() -> None:
    # загрузка токена
    load_dotenv('.env')
    token = os.getenv('TOKEN_API')
    # созадание объекта, наследуемого класс Bot
    bot = Bot(token)
    # созадание объекта, наследуемого класс Dispatcher
    dp = Dispatcher()
    # создание объекта, отвечающего за очереди
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    # регестрация обработчкиков
    rt = register_router()
    dp.include_router(rt)
    # регестрация очереди
    register_scheduler(scheduler)

    # регестрация обработчкиков

    try:
        # запуск работы очереди
        scheduler.start()
        # запуск работы бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    # если файл main.py запускается из терминала,
    # то запустить асинхронную функцию main
    asyncio.run(main())
