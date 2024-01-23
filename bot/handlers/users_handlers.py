from aiogram import types, Dispatcher


from bot.parser.parser import get_studentdiary, now_lesson
from bot.database.db import create_tables, update_data

from bot.database.gets import get_homework, nxtlessn, call_schedule, subjects_schedule

import datetime


async def cmd_start(msg: types.Message) -> None:
    print('id:', msg.from_user.id)
    reply_text = f'привет, {msg.from_user.first_name}'
    await msg.answer(
        text=reply_text,
        reply=True,
        # reply_markup=get_main_ikb()
    )


async def listening(msg: types.Message) -> None:
    if msg.from_user.id != 1277756013:
        return
    if msg.text.startswith('бот'):
        command = msg.text[3:]
        print(command)

    await msg.answer(
        text=msg.text
    )


async def studentdiary(msg: types.Message) -> None:
    if msg.from_user.id != 1277756013:
        return

    await msg.answer('Ваш запрос в обработке...')

    diary = get_studentdiary()

    message = 'Дневник на текущую неделю'

    await msg.answer(message)

    for day in diary:
        text = f"{day}\n\n"
        for num_sub in diary[day]:
            if diary[day][num_sub] == []:
                text += f'{num_sub}| нет урока\n\n'
                continue
            subject = diary[day][num_sub][0]
            time = diary[day][num_sub][1]
            text += f'{num_sub} | {subject} | {time}\n'
            if len(diary[day][num_sub]) == 3:
                homework = diary[day][num_sub][2]
                text += f'     Д/З: {homework}\n'
            text += '\n'

        await msg.answer(text=text)


async def next_lesson(msg: types.Message) -> None:
    await msg.answer('Ваш запрос в обработке...', reply=True)

    time, subject = now_lesson()

    message = 'Сделующий / Текущий урок:\n\n'
    message += f'{subject}\n'
    message += time

    await msg.answer(
        text=message,
        reply=True
    )


async def update_database(msg: types.Message) -> None:
    await msg.answer('Ваш запрос в обработке...', reply=True)
    create_tables()
    update_data()
    await msg.answer('База данных успешно обновлена!', reply=True)


async def homework(msg: types.Message) -> None:
    await msg.answer('Ваш запрос в обработке...', reply=True)

    args = msg.get_args()
    homework_data = get_homework()

    if len(args) != 0:
        try:
            datetime.datetime.strptime(args, '%d.%m.%Y').date()
            homework_data = get_homework(args)
        except Exception as e:
            print(e)
            await msg.answer('Введите дату в формате DD.MM.YYYY')
            return

    for day in homework_data:
        text = 'Домашнее задание на '
        text += day
        for hws in homework_data[day]:
            sub_name = hws[0]
            sub_content = hws[1]

            text += f'\n\n{sub_name}: {sub_content}'

        await msg.answer(text=text)


async def lesson_now(msg: types.Message) -> None:

    data = nxtlessn()
    subject = data['subject_name']
    timestart = data['timestart']
    timeend = data['timeend']
    studyroom = data['studyroom']

    time = f'{timestart} - {timeend}'

    message = 'Сделующий / Текущий урок:\n\n'
    message += f'{subject}\n'
    message += f'{time}\n'
    message += f' каб. {studyroom}'

    await msg.answer(
        text=message,
        reply=True
    )


async def calls(msg: types.Message) -> None:
    calls = call_schedule()
    text = 'Расписание звонков\n\n'
    for call in calls:
        timestart = calls[call]['timestart']
        timeend = calls[call]['timeend']
        text += f'{call}. {timestart} - {timeend}\n'

    await msg.answer(
        text=text,
        reply=True
    )


async def schedule(msg: types.Message) -> None:

    args = msg.get_args()
    data = subjects_schedule()

    if len(args) != 0:
        try:
            datetime.datetime.strptime(args, '%d.%m.%Y').date()
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

    await msg.answer(
        text=text,
        reply=True
    )


def register_user_handlers(dp: Dispatcher) -> None:

    dp.register_message_handler(cmd_start, commands=['start'])
    # dp.register_message_handler(studentdiary, commands=['diary'])
    dp.register_message_handler(lesson_now, commands=['lesson_now'])
    dp.register_message_handler(homework, commands=['homework'])
    dp.register_message_handler(update_database, commands=['update_database'])
    dp.register_message_handler(calls, commands=['calls'])
    dp.register_message_handler(schedule, commands=['schedule'])
    # dp.register_message_handler(listening, lambda msg: msg.text)
