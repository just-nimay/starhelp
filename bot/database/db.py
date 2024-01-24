# Импорт необходимых библиотек
import pymysql.cursors
import os
import sys

from dotenv import load_dotenv

# Импорт функции, получающей данные с сайта
from bot.parser.parser import get_studentdiary

# функция, осуществляющая подключение к базе данных


def connect_to_database() -> pymysql.connect:
    # загрузка данных для подключения к базе данных
    load_dotenv('.env')

    # попытка подключения к БД
    try:

        ''' CREATE DATABASE IF NOT EXISTS `starhelp` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */ '''

        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
        )
        # возвращение подключения
        return connection
    # При возникновении ошибки, возвращать текст об ошибке
    except Exception as e:
        print('err:', e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# функция, создающая таблицы в БВ
def create_tables():
    try:
        # подключение к БД
        connect = connect_to_database()
        # Делаем возможность взаимодействия с БД
        with connect.cursor() as cursor:

            # Создание таблицы "date" если той не существует
            # В этой таблице хранятся данные об учебных датах
            table_date = '''
            CREATE TABLE IF NOT EXISTS `date` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `year` int(11) NOT NULL,
                `day` int(11) NOT NULL,
                `month` varchar(20) NOT NULL,
                `weekday` varchar(20) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_date)
            connect.commit()

            # Создание таблицы "subject" если той не существует
            # В этой таблице хранятся данные об существующих предметах
            table_subjects = '''
            CREATE TABLE IF NOT EXISTS `subject` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `name` varchar(50) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_subjects)
            connect.commit()

            # Создание таблицы "homework" если той не существует
            # в этой таблице хранятся данные всех домашних заданий
            # Каждая запись связана с предметом из таблицы "subject"
            # а так же с таблицей "date"
            table_homework = '''
            CREATE TABLE IF NOT EXISTS `homework` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `subject_id` int(11) DEFAULT NULL,
                `date_id` int(11) DEFAULT NULL,
                `content` text,
                PRIMARY KEY (`id`),
                KEY `subject_id` (`subject_id`),
                CONSTRAINT `homework_ibfk_1`
                FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE CASCADE,
                CONSTRAINT `homework_date_ibfk_1`
                FOREIGN KEY (`date_id`) REFERENCES `date` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_homework)
            connect.commit()

            # Создание таблицы "number_subject" если той не существует
            # в этой таблице хранится информация о расписании времени звонков
            table_num_sub = '''
            CREATE TABLE IF NOT EXISTS `number_subject` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `number` int(11) DEFAULT NULL,
                `timestart` time DEFAULT NULL,
                `timeend` time DEFAULT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_num_sub)
            connect.commit()

            # значения для таблицы "number_subject"
            values = [
                [1, '8:00', '8:40'],
                [2, '8:50', '9:30'],
                [3, '9:50', '10:30'],
                [4, '10:40', '11:20'],
                [5, '11:30', '12:10'],
                [6, '12:20', '13:00'],
                [7, '13:10', '13:50'],
                [8, '14:00', '14:40'],
                [9, '14:50', '15:30'],
                [10, '15:50', '16:30']
            ]

            # внесение значений
            for value in values:
                check_exists = '''
                select exists(
                    select id from number_subject where number = %s
                )
                '''
                cursor.execute(check_exists, value[0])
                response = cursor.fetchone()[0]
                if response:
                    pass
                else:
                    request = '''
                    INSERT INTO `number_subject` (number, timestart, timeend)
                    VALUES (%s, %s, %s)
                    '''

                    cursor.execute(request, (value[0], value[1], value[2]))
                    connect.commit()

            # Создание таблицы "lessons" если той не существует
            # в этой таблице хранится данные о проводимых занятиях
            # связана с таблицей "subject"
            # связана с таблицей "date"
            # связана с таблицей "number_subject"
            table_lessons = '''
            CREATE TABLE IF NOT EXISTS `lessons` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `date_id` int(11) DEFAULT NULL,
                `subject_id` int(11) DEFAULT NULL,
                `homework_id` int(11) DEFAULT NULL,
                `number_subject_id` int(11) DEFAULT NULL,
                `studyroom` varchar(50) DEFAULT NULL,
                PRIMARY KEY (`id`),
                KEY `subject_id` (`subject_id`),
                KEY `date_id` (`date_id`),
                KEY `homework_id` (`homework_id`),
                KEY `number_subject_id` (`number_subject_id`),
                CONSTRAINT `lessons_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE CASCADE,
                CONSTRAINT `lessons_ibfk_2` FOREIGN KEY (`date_id`) REFERENCES `date` (`id`) ON DELETE CASCADE,
                CONSTRAINT `lessons_ibfk_3` FOREIGN KEY (`homework_id`) REFERENCES `homework` (`id`) ON DELETE CASCADE,
                CONSTRAINT `lessons_ibfk_4` FOREIGN KEY (`number_subject_id`) REFERENCES `number_subject` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_lessons)
            connect.commit()

            # завершаем сессию
            cursor.close()
            connect.close()
    except Exception as e:
        print('err:', e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# функция добавления нового дня в таблицу "date"
def add_date(year, day, month, weekday):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            # проверка на существование записи
            check_exists = f'''
                select exists(
                    SELECT id FROM date WHERE year = {year} AND day = {day} AND month = "{month}"
                );
                '''

            cursor.execute(check_exists)
            response = cursor.fetchone()[0]
            # если запись существует то ничего не делаем
            if response:
                pass
            else:
                # если же записи все же нет, то добавляем
                request = f'''
                INSERT INTO `date` (year, day, month, weekday)
                VALUES ({year}, {day}, "{month}", "{weekday}");
                '''

                cursor.execute(request)
                connect.commit()

            # получение индентификатора созданной записи
            get_date_id_request = '''
            SELECT id FROM date WHERE year = %s AND day = %s AND month = %s;
            '''

            cursor.execute(get_date_id_request,
                           (year, day, month))

            date_id = cursor.fetchone()[0]

            # завершение сесси
            cursor.close()
            connect.close()

            # возвращаем id
            return date_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# добавление предмета в таблицу "subject"
# по характеру работы подобна предыдущей функции
def add_subject(name):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:
            check_exists = '''
            select exists (
                SELECT id FROM subject WHERE name = %s
            );
            '''
            cursor.execute(check_exists, name)
            response = cursor.fetchone()[0]
            if response:
                pass
            else:
                request = '''
                INSERT INTO `subject` (name)
                    VALUES (%s)
                '''

                cursor.execute(request, (name))
                connect.commit()

            get_subject_id_request = '''
            SELECT id FROM subject WHERE name = %s;
            '''

            cursor.execute(get_subject_id_request,
                           (name))

            subject_id = cursor.fetchone()[0]

            cursor.close()
            connect.close()

            return subject_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# добавление предмета в таблицу "homework"
def add_homework(subject_id, date_id, content):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            if content is None:
                # если данных о домашнем задании нет
                data = (subject_id, date_id, None)
            else:
                # если данные о домашнем задании есть
                data = (subject_id, date_id, content)

            check_exists = '''
            select exists (
                SELECT id FROM homework WHERE subject_id = %s AND date_id = %s
            );
            '''
            # проверка существования записи
            cursor.execute(check_exists, (subject_id, date_id))
            response = cursor.fetchone()[0]
            if response:
                # если запись существует, получаем id этой записи
                get_date_id_request = '''
            SELECT id FROM homework WHERE subject_id = %s AND date_id = %s;
            '''
                cursor.execute(get_date_id_request,
                               (subject_id, date_id))

                homework_id = cursor.fetchone()
                print('IN add_homework', homework_id)

                # обновляем данные о домашнем задании
                request = '''
                update homework set content = %s where id = %s
                '''
                cursor.execute(request, (content, homework_id))
                connect.commit()

            # если записи не существует
            else:
                # добавление записи
                request = '''
                INSERT INTO `homework` (subject_id, date_id, content)
                VALUES (%s, %s, %s);
                '''

                cursor.execute(request, data)
                connect.commit()
            # получение id записи
            get_date_id_request = '''
            SELECT id FROM homework WHERE subject_id = %s AND date_id = %s;
            '''

            cursor.execute(get_date_id_request,
                           (subject_id, date_id))

            homework_id = cursor.fetchone()
            print('IN add_homework', homework_id)

            # завершение сессии
            cursor.close()
            connect.close()

            return homework_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# добавление занятия в таблицу "lessons"
# по характеру работы подобна предыдущей функции
def add_lesson(date_id, subject_id, homework_id, num_sub, studyroom):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            check_exists = '''
            select exists (
                SELECT id FROM lessons WHERE date_id = %s AND subject_id = %s AND homework_id = %s AND number_subject_id = %s
            );
            '''
            cursor.execute(check_exists, (date_id, subject_id,
                           homework_id, num_sub))
            response = cursor.fetchone()[0]
            if response:
                pass
            else:
                request = '''
                INSERT INTO `lessons` (date_id, subject_id, homework_id, number_subject_id, studyroom)
                VALUES (%s, %s, %s, %s, %s)
                '''
                if studyroom is None:
                    data = (date_id, subject_id, homework_id, num_sub, None)
                else:
                    data = (date_id, subject_id,
                            homework_id, num_sub, studyroom)

                cursor.execute(request, data)
                connect.commit()

            get_lesson_id_request = '''
            SELECT id FROM lessons WHERE date_id = %s AND subject_id = %s AND homework_id = %s AND number_subject_id = %s AND studyroom = %s;
            '''

            cursor.execute(get_lesson_id_request,
                           (date_id, subject_id, homework_id, num_sub, studyroom))

            lesson_id = cursor.fetchone()[0]

            cursor.close()
            connect.close()

            return lesson_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


# функция обновления данных
# получает данные с сайта и постепенно
# проводит заполнение БД используя функции выше
def update_data():
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            diary = get_studentdiary()

            for day in diary:
                print('\n\n', day)
                for num_sub in diary[day]:
                    print(num_sub, diary[day][num_sub])

            for day in diary:
                weekday, date = day.split(',')
                date_day, date_mounth, date_year = date[1:-3].split(' ')
                date_id = add_date(date_year, date_day, date_mounth, weekday)
                for num_sub in diary[day]:

                    subject = None
                    studyroom = None
                    homework = None

                    if diary[day][num_sub] == []:
                        continue

                    subject = diary[day][num_sub][0]
                    value = diary[day][num_sub][1]
                    print(
                        f"num_sub: {num_sub}|subject: {subject}| value: {value}|")

                    if len(diary[day][num_sub][1].split(' , ')) == 2:
                        studyroom = diary[day][num_sub][1].split(' , ')[1]

                    if len(diary[day][num_sub]) == 3:
                        homework = diary[day][num_sub][2]

                    subject_id = add_subject(subject)
                    print(
                        f'SUBJECT {subject}:{subject_id}  HW: {homework}ADDED')
                    homework_id = add_homework(subject_id, date_id, homework)
                    print(f'HOMEWORK {homework_id} ADDED')

                    lesson_id = add_lesson(date_id, subject_id,
                                           homework_id, num_sub, studyroom)
                    print(f'LESSON {lesson_id} ADDED')

            cursor.close()
            connect.close()

    except Exception as e:
        print('err:', e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
