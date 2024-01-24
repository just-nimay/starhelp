import pymysql.cursors
import os
import datetime

from bot.database.db import connect_to_database
from bot.parser.parser import transform_date


def get_date_id(year, day, month) -> int:
    connection = connect_to_database()
    with connection.cursor() as cursor:
        get_req = f'''
        select id from date where year={year} and day={day} and month="{month}";
        '''

        cursor.execute(get_req)
        date_id = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return date_id


def get_subject_name(subject_id) -> str:
    connection = connect_to_database()
    with connection.cursor() as cursor:
        get_req = f'''
        select name from subject where id={subject_id};
        '''

        cursor.execute(get_req)
        subject_name = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return subject_name


def get_homework(date=None) -> dict:
    if date is None:
        date = datetime.datetime.today()
        date += datetime.timedelta(days=1)
        date = date.strftime('%d.%m.%Y')

    day = transform_date(date)
    weekday, date = day.split(',')
    date_day, date_mounth, date_year = date[1:-3].split(' ')

    date_id = get_date_id(date_year, date_day, date_mounth)

    ready = {day: []}

    connection = connect_to_database()
    with connection.cursor() as cursor:
        get_req = f'''
        select subject_id, content from homework where date_id = {date_id};
        '''
        cursor.execute(get_req)
        data = cursor.fetchall()
        for hw in data:
            subject_name = get_subject_name(hw[0])
            content = 'Нет задания'
            if len(hw) == 2:
                content = hw[1]
                if content is None:
                    content = 'Нет задания'
            ready[day].append([subject_name, content])

        cursor.close()
        connection.close()

    print(ready)
    return ready


def call_schedule() -> dict:
    connection = connect_to_database()
    with connection.cursor() as cursor:
        get_req = f'''
        select number, timestart, timeend from number_subject;
        '''
        cursor.execute(get_req)
        data = cursor.fetchall()

        ready = {}
        for row in data:
            number = row[0]
            timestart = row[1]
            timeend = row[2]

            ready[number] = {'timestart': timestart, 'timeend': timeend}

        cursor.close()
        connection.close()

        return ready


def nxtlessn(date=None) -> dict:
    if date is None:
        time = datetime.datetime.now().time()
        date = datetime.datetime.today()
        date = date.strftime('%d.%m.%Y')

    time = datetime.datetime.now().time()
    day = transform_date(date)
    print(date)
    print('DAY', day)
    weekday, datef = day.split(',')
    date_day, date_mounth, date_year = datef[1:-3].split(' ')

    date_id = get_date_id(date_year, date_day, date_mounth)

    calls = call_schedule()

    timemax = str(calls[9]['timeend'])
    timedate = datetime.datetime.strptime(
        f'{date} {timemax}', '%d.%m.%Y %H:%M:%S')
    now = datetime.datetime.now()
    if timedate < now:
        date = datetime.datetime.today()
        date += datetime.timedelta(days=1)
        date = date.strftime('%d.%m.%Y')
        data = nxtlessn(date=date)
        return data
    print('YES YES YES')
    for call in calls:
        timestart = calls[call]['timestart']
        timeend = str(calls[call]['timeend'])
        timeend_date = datetime.datetime.strptime(
            f'{date} {timeend}', '%d.%m.%Y %H:%M:%S')
        if timeend_date > now:
            number_subject_id = call

            connection = connect_to_database()
            with connection.cursor() as cursor:

                req = f'''
                select subject_id, studyroom from lessons where date_id={date_id} and
                number_subject_id = {number_subject_id};
                '''
                cursor.execute(req)
                data = cursor.fetchall()
                for row in data:
                    subject_name = get_subject_name(row[0])
                    studyroom = row[1]

                    cursor.close()
                    connection.close()

                    return {'subject_name': subject_name,
                            'studyroom': studyroom,
                            'timestart': timestart,
                            'timeend': timeend}


def subjects_schedule(date=None) -> dict:
    if date is None:
        date = datetime.datetime.today()
        date = date.strftime('%d.%m.%Y')

    day = transform_date(date)
    weekday, date = day.split(',')
    date_day, date_mounth, date_year = date[1:-3].split(' ')

    date_id = get_date_id(date_year, date_day, date_mounth)

    connection = connect_to_database()
    with connection.cursor() as cursor:

        req = f'''
        select subject_id, number_subject_id, studyroom from lessons where date_id = {date_id};
        '''

        cursor.execute(req)
        data = cursor.fetchall()

        ready = {day: {}}

        for row in data:
            subject_name = get_subject_name(row[0])
            number_subject_id = row[1]

            studyroom = row[2]
            if studyroom is None:
                studyroom = 'Уточните у проеподавателя'

            ready[day][number_subject_id] = {
                'subject_name': subject_name,
                'studyroom': studyroom}

        cursor.close()
        connection.close()

        return ready
