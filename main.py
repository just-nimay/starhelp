# Импортируем необходимые библиотеки
import asyncio
import os


from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# импортируем функцию, регистрирующую обработчики команд и сообщений
from bot.handlers.users_handlers import register_user_handlers
# импортируем функцию, регистрирующую очереди повторяющихся функций
from bot.scheduler.users_schedulers import register_user_scheduler


# функция регестрации обработчиков
def register_handler(dp: Dispatcher) -> None:
    register_user_handlers(dp)


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
    dp = Dispatcher(bot)
    # создание объекта, отвечающего за очереди
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    # регестрация обработчкиков
    register_handler(dp)
    # регестрация очереди
    register_scheduler(scheduler)

    try:
        # запуск работы очереди
        scheduler.start()
        # запуск работы бота
        await dp.start_polling()
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    # если файл main.py запускается из терминала,
    # то запустить асинхронную функцию main
    asyncio.run(main())
