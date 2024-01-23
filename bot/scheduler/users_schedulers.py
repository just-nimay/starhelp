from bot.database.db import update_data


async def updating_database() -> None:
    print('YES YES YES YES YES YES  YES YES YES')
    update_data()


def register_user_scheduler(scheduler) -> None:
    scheduler.add_job(updating_database, "interval", minutes=30,
                      start_date='2023-07-20 07:30:00', args=())
