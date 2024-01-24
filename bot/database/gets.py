# импорт необходимых библиотек
import datetime

# получение функции, создающей подключение к БД
from bot.database.db import connect_to_database
# Получение функции, преобразовывающей дату
from bot.parser.parser import transform_date


# получение id даты, по году, дню и месяцу
def get_date_id(year, day, month) -> int:
    # создания соединения с БД
    connection = connect_to_database()
    with connection.cursor() as cursor:
        # формирование запроса к БД
        get_req = f'''
        select id from date where year={year} and day={day} and month="{month}";
        '''
        # получение ответа от базы данных
        cursor.execute(get_req)
        date_id = cursor.fetchone()[0]

        # завершение сессии
        cursor.close()
        connection.close()

        # возвращение id даты
        return date_id


# получение названия предмета по id
# функция подобна предыдущей
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


# получение домашнего задания на дату
# если фунции не сообщился аргумент date,
# то пол умолчанию date=None
def get_homework(date=None) -> dict:
    # Если аргумент не был сообщен
    if date is None:
        # формирование завтрешней даты в формате ДД.ММ.ГГГГ
        date = datetime.datetime.today()
        date += datetime.timedelta(days=1)
        date = date.strftime('%d.%m.%Y')
    # преобразование даты
    day = transform_date(date)
    # получение дня, месяца и года даты
    weekday, date = day.split(',')
    date_day, date_mounth, date_year = date[1:-3].split(' ')
    # получение id даты
    date_id = get_date_id(date_year, date_day, date_mounth)

    # создание шаблона ответа
    ready = {day: []}

    # подключение к БД
    connection = connect_to_database()
    with connection.cursor() as cursor:
        # получение id предметта и домашнего задания из БД
        # по определенному id даты
        get_req = f'''
        select subject_id, content from homework where date_id = {date_id};
        '''
        # получение всех предметов на дату
        cursor.execute(get_req)
        data = cursor.fetchall()
        # формирование ответа
        for hw in data:
            subject_name = get_subject_name(hw[0])
            content = 'Нет задания'
            if len(hw) == 2:
                content = hw[1]
                if content is None:
                    content = 'Нет задания'
            ready[day].append([subject_name, content])
        # завершение сессии
        cursor.close()
        connection.close()
    # возвращение домашнего задания
    print(ready)
    return ready


# функция получения расписания занятий
# подобна функции get_date_id()
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


# функция получения текущего или следующего урока
# может принимать дату
def nxtlessn(date=None) -> dict:
    if date is None:
        # если дата не была передана
        # получение текущей даты
        time = datetime.datetime.now().time()
        date = datetime.datetime.today()
        date = date.strftime('%d.%m.%Y')

    # получение текущего времени
    time = datetime.datetime.now().time()
    # преобразование даты
    day = transform_date(date)
    print(date)
    print('DAY', day)
    # получение id даты
    weekday, datef = day.split(',')
    date_day, date_mounth, date_year = datef[1:-3].split(' ')

    date_id = get_date_id(date_year, date_day, date_mounth)

    #  получение расписания
    calls = call_schedule()
    # время, в которое заканчивается 10 урок
    timemax = str(calls[9]['timeend'])
    # дата и время, в которые заканчивается 10 урок
    timedate = datetime.datetime.strptime(
        f'{date} {timemax}', '%d.%m.%Y %H:%M:%S')
    # текущие дата и время
    now = datetime.datetime.now()
    if timedate < now:
        # если текущее время больше времени
        # сегодняшнего последнего урока то
        # вызов этой же функции, но с завтрешней датой
        date = datetime.datetime.today()
        date += datetime.timedelta(days=1)
        date = date.strftime('%d.%m.%Y')
        data = nxtlessn(date=date)
        # возвращение данных о текущем или следующем уроке
        return data

    # пребор каждого звонка
    for call in calls:
        # время начала урока
        timestart = calls[call]['timestart']
        # время окончания урока
        timeend = str(calls[call]['timeend'])
        # дата оканчания урока
        timeend_date = datetime.datetime.strptime(
            f'{date} {timeend}', '%d.%m.%Y %H:%M:%S')
        if timeend_date > now:
            # если дата оканчания урока больше сегодняшней даты то
            # задается порядковый номер урока
            number_subject_id = call
            # создания соединения с БД
            connection = connect_to_database()
            with connection.cursor() as cursor:
                # получение id предмета и кабинета из таблицы всех занятий,
                # где id даты равен заданому и номер урока равен заданному
                req = f'''
                select subject_id, studyroom from lessons where date_id={date_id} and
                number_subject_id = {number_subject_id};
                '''
                # получение данных о предмете
                cursor.execute(req)
                data = cursor.fetchall()
                for row in data:
                    subject_name = get_subject_name(row[0])
                    studyroom = row[1]

                    # завершение сессии
                    cursor.close()
                    connection.close()
                    # возвращение данных о текущем или следующем уроке
                    return {'subject_name': subject_name,
                            'studyroom': studyroom,
                            'timestart': timestart,
                            'timeend': timeend}


# функция получения расписания занятий на день
# подобна предыдущим
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
                # если кабинет не назначен
                studyroom = 'Уточните у проеподавателя'

            ready[day][number_subject_id] = {
                'subject_name': subject_name,
                'studyroom': studyroom}

        cursor.close()
        connection.close()

        return ready
