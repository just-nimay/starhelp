import pymysql.cursors
import os
import sys

from dotenv import load_dotenv

from bot.parser.parser import get_studentdiary


def connect_to_database() -> pymysql.connect:
    load_dotenv('.env')
    try:

        ''' CREATE DATABASE IF NOT EXISTS `starhelp` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */ '''

        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
        )

        return connection
    except Exception as e:
        print('err:', e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


def create_tables():
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

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

            table_subjects = '''
            CREATE TABLE IF NOT EXISTS `subject` (
                `id` int(11) NOT NULL AUTO_INCREMENT,
                `name` varchar(50) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            '''
            cursor.execute(table_subjects)
            connect.commit()

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
                [10, '15:50', '14:30']
            ]

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

            cursor.close()
            connect.close()
    except Exception as e:
        print('err:', e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


def add_date(year, day, month, weekday):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            check_exists = f'''
                select exists(
                    SELECT id FROM date WHERE year = {year} AND day = {day} AND month = "{month}"
                );
                '''

            print('HELLOLEWFKEWFJD\n\n' + check_exists + '\n\n')
            cursor.execute(check_exists)
            response = cursor.fetchone()[0]
            if response:
                pass
            else:
                request = f'''
                INSERT INTO `date` (year, day, month, weekday)
                VALUES ({year}, {day}, "{month}", "{weekday}");
                '''

                cursor.execute(request)
                connect.commit()

            get_date_id_request = '''
            SELECT id FROM date WHERE year = %s AND day = %s AND month = %s;
            '''

            cursor.execute(get_date_id_request,
                           (year, day, month))

            date_id = cursor.fetchone()[0]

            cursor.close()
            connect.close()

            return date_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


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


def add_homework(subject_id, date_id, content):
    try:
        connect = connect_to_database()

        with connect.cursor() as cursor:

            if content is None:
                data = (subject_id, date_id, None)
            else:
                data = (subject_id, date_id, content)

            check_exists = '''
            select exists (
                SELECT id FROM homework WHERE subject_id = %s AND date_id = %s
            );
            '''
            cursor.execute(check_exists, (subject_id, date_id))
            response = cursor.fetchone()[0]
            if response:
                get_date_id_request = '''
            SELECT id FROM homework WHERE subject_id = %s AND date_id = %s;
            '''
                cursor.execute(get_date_id_request,
                               (subject_id, date_id))

                homework_id = cursor.fetchone()
                print('IN add_homework', homework_id)

                request = '''
                update homework set content = %s where id = %s
                '''
                cursor.execute(request, (content, homework_id))
                connect.commit()

            else:

                request = '''
                INSERT INTO `homework` (subject_id, date_id, content)
                VALUES (%s, %s, %s);
                '''

                cursor.execute(request, data)
                connect.commit()

            get_date_id_request = '''
            SELECT id FROM homework WHERE subject_id = %s AND date_id = %s;
            '''

            cursor.execute(get_date_id_request,
                           (subject_id, date_id))

            homework_id = cursor.fetchone()
            print('IN add_homework', homework_id)

            cursor.close()
            connect.close()

            return homework_id
    except Exception as e:
        print(e)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))


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
