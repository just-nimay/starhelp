# импорт функции, которая обновляет базу данных
from bot.database.db import update_data


# асинхронная функциия (значит запускается
# паралельно с другими процессами)
async def updating_database() -> None:
    # вызов функции обновления
    update_data()


# функция регистрации всех очередей
def register_user_scheduler(scheduler) -> None:
    # добавление нового вызова функции
    # updating_database() с интервалом 30 минут
    scheduler.add_job(updating_database, "interval", minutes=30,
                      start_date='2023-07-20 07:30:00', args=())
