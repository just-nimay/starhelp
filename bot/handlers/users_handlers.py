# импорт необходимых библиотек
from aiogram import types, Router
from aiogram.filters import Command, CommandObject

# импорт функций, создающих и обновляющих БД
from bot.database.db import create_tables, update_data

# импорт функций, возвращающих данные из БД
from bot.database.gets import get_homework, nxtlessn, call_schedule, subjects_schedule

import datetime

# перечень команд, на кторые бот будет реагировать
BOT_CMDS = {
    'скинь дз': 1,
    'пришли дз': 1,
    "отправь дз": 1,
    "отправь домашнее задание": 1,
    "скинь домашнее задание": 1,
    "дз скинь": 1,

    "какой щас урок": 2,
    "какой щас урок?": 2,
    "что за урок": 2,
    "что за урок щас": 2,
    "какой сейчас урок": 2,
    "какой сейчас урок?": 2,
    "что за урок сейчас": 2,
    "какой ща урок": 2,
    "че ща за урок": 2,
    "че за урок ща": 2,

    "какой сдедующий урок": 2,
    "какой сдедующий урок?": 2,
    "что за урок сдедующий": 2,
    'следующий урок': 2,

    "когда звонок": 3,
    "когда звонок?": 3,

    "скинь расписание": 4,
    "какое расписание": 4,
    "какое расписание сегодня": 4,

}


# фукнция, отвечающая за команду /start
# примимает сообщение
async def cmd_start(msg: types.Message) -> None:
    # вывод в терминал id отправителя
    print('id:', msg.from_user.id)
    # текст сообщения, которое бот отправит
    reply_text = f'привет, {msg.from_user.first_name}'
    # ответ на команду
    await msg.reply(
        text=reply_text
    )


# функция, отвечающая за команду /update_database
async def update_database(msg: types.Message) -> None:
    # отправка сообщения
    await msg.reply('Ваш запрос в обработке...')
    # вызов фунции, которая создаст таблицы, если их еще нет
    create_tables()
    # вывоз функции, которая обнавляет данные в БД
    update_data()
    # отправка сообщения
    await msg.answer('База данных успешно обновлена!')


# функция, отвечающая за команду /homework
# эта команда может примимать аргументы от пользователя: /homework 01.01.2024
# так же эта функция может приять аргумент call, но если его не передать,
# то будет присвоено переменно call значение False
async def homework(msg: types.Message, command: CommandObject, call=False) -> None:
    await msg.reply('Ваш запрос в обработке...')
    # проверить какой сегодня день
    date = datetime.datetime.today()
    week_day = date.weekday()

    # по умолчанию аргумент команды пуст
    args = ''
    # по умолчанию данные пусты
    homework_data = {}

    # если переменной call дали значение True,
    # то значит, что функцию homework вызывают из другой фунции

    # В случае, если все же функция не вызывалась из дугой функции,
    # то значит что команда может именть аргументы
    if not call:
        if command.args is not None:
            args = command.args

    if len(args) != 0:
        # В случае, если агрумент есть, то попытаться
        # преобразовать его в дату, если возникнет ошибка, то
        try:
            day = datetime.datetime.strptime(args, '%d.%m.%Y')
            if day.weekday() == 6:
                await msg.reply(text='Указанная дата - воскресенье, какая домашка?')
                return
            homework_data = get_homework(day)
        except Exception as e:
            print(e)
            # отправить пользователю сообщение о
            # правильном фомате аргумента
            await msg.answer('Введите дату в формате DD.MM.YYYY')
            return
    # если завтра воскреснье, то
    # получить домашнее задание на понедельник
    elif week_day == 6 or week_day == 5:
        print('YESS')

        if week_day == 6:
            date += datetime.timedelta(days=1)
        if week_day == 5:
            date += datetime.timedelta(days=2)

        date = date.strftime('%d.%m.%Y')
        homework_data = get_homework(date)
    else:
        # В случае, если агрумента нет
        homework_data = get_homework()

    # формирование текста сообщения с домашним заданием
    for day in homework_data:
        text = 'Домашнее задание на '
        text += day
        for hws in homework_data[day]:
            sub_name = hws[0]
            sub_content = hws[1]

            text += f'\n\n{sub_name}: {sub_content}'
        # отправка сообщения с текстом
        await msg.answer(text=text)


# функция, отвечающая за команду /lesson_now
async def lesson_now(msg: types.Message) -> None:

    # если сегодня воскресенье,
    # то сообщить что уроков нет и
    # закончить выполнение команды
    week_day = datetime.datetime.now().weekday()
    if week_day == 6:
        await msg.reply(text='Отдыхай, сегодня воскресенье')
        return

    # получение данных о следующем уроке
    data = nxtlessn()
    # Если функц. вернула Null, то значит сегодня
    # суббота и уроков больше нет
    if data is None:
        await msg.reply(text='Отдыхай, следующий урок нескоро')
        return
    print("DATA", data)

    # формирование текста сообщения
    subject = data['subject_name']
    timestart = data['timestart']
    timeend = data['timeend']
    studyroom = data['studyroom']

    time = f'{timestart} - {timeend}'

    message = 'Сделующий / Текущий урок:\n\n'
    message += f'{subject}\n'
    message += f'{time}\n'
    message += f' каб. {studyroom}'

    # отправка сообщения с текстом
    await msg.answer(
        text=message,
        reply=True
    )


# функция, отвечающая за команду /calls
async def calls(msg: types.Message) -> None:
    # получение данных о звонках
    calls = call_schedule()
    # формирование сообщения
    text = 'Расписание звонков\n\n'
    for call in calls:
        timestart = calls[call]['timestart']
        timeend = calls[call]['timeend']
        text += f'{call}. {timestart} - {timeend}\n'

    # отправка сообщения
    await msg.reply(
        text=text
    )


# функция, отвечающая за команду /schedule
# подобна функции homework()
async def schedule(msg: types.Message, command: CommandObject, call=False) -> None:
    # если сегодня воскресенье,
    # то сообщить что уроков нет и
    # закончить выполнение команды
    week_day = datetime.datetime.now().weekday()
    if week_day == 6:
        await msg.reply(text='Сегодня по расписанию отдыхать')
        return

    args = ''
    if not call:
        if command.args is not None:
            args = command.args
    data = subjects_schedule()

    if len(args) != 0:
        try:
            day = datetime.datetime.strptime(args, '%d.%m.%Y')
            if day.weekday() == 6:
                await msg.answer(text='Указанная дата - воскресенье, какое расписание?')
                return
            data = subjects_schedule(args)
        except Exception as e:
            print(e)
            await msg.answer('Введите дату в формате DD.MM.YYYY')
            return

    text = 'Расписание уроков на '
    for day in data:
        text += f'{day}\n\n'
        for sub_numb in data[day]:
            subject_name = data[day][sub_numb]['subject_name']
            studyroom = data[day][sub_numb]['studyroom']

            text += f'{sub_numb}. {subject_name}. каб. {studyroom}\n'

    await msg.reply(
        text=text
    )


# функция, читающая каждое сообщение
async def listening(msg: types.Message) -> None:
    # получение первого солова сообщения,
    # форматирование текста
    first_word = msg.text.split(' ')[0].lower()
    if ',' in first_word:
        first_word = first_word.replace(',', '')

    # если первое слово - обращение к боту то продолжает работу
    # с сообщением
    if first_word in ['бот', 'ботик', 'ботяра']:
        # получение текста команды
        cmd = msg.text.replace(first_word, '').replace(
            ',', '').lower().lstrip()
        print(cmd)
        # проход по извезным текстовым командам
        for bot_cmd in BOT_CMDS:
            # если есть совпадение
            if cmd == bot_cmd:
                # получение номера команды,
                # и в зависимости от номера
                # вызов фукнций команд
                command = BOT_CMDS[bot_cmd]
                if command == 1:
                    cmdObj = CommandObject()
                    await homework(msg, command=cmdObj, call=True)
                    return
                if command == 2:
                    await lesson_now(msg)
                    return
                if command == 3:
                    await calls(msg)
                    return
                if command == 4:
                    cmdObj = CommandObject()
                    await schedule(msg, command=cmdObj, call=True)
                    return
        # если команда не подошла, отпавить сообщение
        await msg.reply(
            text='Команда не распознана'
        )


# функция, регестрирущая команды
def register_user_router() -> Router:
    router = Router()

    router.message.register(cmd_start, Command('start'))
    router.message.register(lesson_now, Command('lesson_now'))
    router.message.register(homework, Command('homework'))
    router.message.register(update_database, Command('update_db'))
    router.message.register(calls, Command('calls'))
    router.message.register(schedule, Command('schedule'))
    router.message.register(listening)

    return router
