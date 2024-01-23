from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


import time as t
import datetime

import os


from dotenv import load_dotenv

WEEKDAYS = ['Понедельник',
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"]


def transform_date(date: datetime) -> str:
    """Transform date from datetime to str.

        :Return:
            ::

                '{week_day}, {day} {months[int(month) - 1]} {year} г.'
        """

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    day, month, year = date.split('.')
    a = datetime.datetime(int(year),
                          int(month),
                          int(day))
    week_day = WEEKDAYS[a.weekday()]

    return f'{week_day}, {day} {months[int(month) - 1]} {year} г.'


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_tag(driver, tag):
    try:
        driver.find_element(By.TAG_NAME, tag)
    except NoSuchElementException:
        return False
    return True


def close_site(page: webdriver.Chrome) -> None:

    if check_exists_by_xpath(page, "//*[contains(text(), 'Выход')]"):
        page.find_element(
            By.XPATH, "//*[contains(text(), 'Выход')]").click()
        t.sleep(0.2)
        page.find_element(
            By.XPATH, "//*[contains(text(), 'Да')]").click()


def check_exists_by_classname(driver, name):
    try:
        driver.find_element(By.CLASS_NAME, name)
    except NoSuchElementException:
        return False
    return True


def get_page(url) -> webdriver.Chrome:
    load_dotenv('.env')

    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome()
    browser.get(url)
    t.sleep(2)

    browser.find_element(By.CLASS_NAME, "select2-selection__arrow").click()

    t.sleep(0.5)
    browser.find_element(
        By.CLASS_NAME, "select2-search__field").send_keys(os.getenv('SGORSO_SCHOOL'))
    t.sleep(0.5)
    browser.find_element(By.CLASS_NAME, "select2-results__option").click()
    t.sleep(0.5)
    browser.find_element(By.NAME, 'loginname').send_keys(os.getenv('SGORSO_LOGIN'))
    t.sleep(0.5)
    browser.find_element(By.NAME, 'password').send_keys(os.getenv('SGORSO_PASS'))
    t.sleep(0.5)
    browser.find_element(By.CLASS_NAME, "primary-button").click()
    t.sleep(0.5)
    if check_exists_by_xpath(browser, "//*[contains(text(), 'Продолжить')]"):
        browser.find_element(
            By.XPATH, "//*[contains(text(), 'Продолжить')]").click()
    t.sleep(2)

    return browser


def get_studentdiary() -> dict:
    url = 'https://sgo.rso23.ru/angular/school/studentdiary/'

    page = get_page(url)
    t.sleep(3)
    data = page.find_elements(By.CLASS_NAME, 'day_table')
    diary = {}
    for day in data:
        trs = day.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')

            if check_exists_by_classname(tr, 'day_name'):
                day = tr.find_element(By.CLASS_NAME, 'day_name').text

                diary[day] = {}

            if check_exists_by_classname(tr, 'num_subject'):
                num_subject = tr.find_element(
                    By.CLASS_NAME, 'num_subject').text
                diary[day][num_subject] = []

            for td in tds:
                if len(td.text) == 0:
                    continue

                if check_exists_by_classname(td, 'subject'):
                    subject = td.find_element(By.CLASS_NAME, 'subject').text
                    if subject not in diary[day][num_subject]:
                        diary[day][num_subject].append(subject)

                if check_exists_by_classname(td, 'time'):
                    time = td.find_element(By.CLASS_NAME, 'time').text
                    if time not in diary[day][num_subject]:
                        diary[day][num_subject].append(time)

                if check_exists_by_tag(td, 'a'):
                    homework = td.find_element(
                        By.TAG_NAME, 'a').text
                    if homework not in diary[day][num_subject]:
                        diary[day][num_subject].append(homework)

    close_site(page)
    page.close()

    return diary

    '''
for day in diary:
    print('\n\n', day)
    for num_sub in diary[day]:
        print(num_sub, diary[day][num_sub])
        
    ------------
    
 Понедельник, 22 января 2024 г.
1 []
2 ['Основы безопасности жизнедеятельности', '08:50 - 09:30 , 301', 'Параграф 18 с. 264-267']
3 ['Математика', '09:50 - 10:30 , 107', 'Выполнить работу на Яклассе https://www.yaklass.ru/TestWork/CopyShared/rmMB5FiMbUCZwGXy5aQ6Fw']
4 ['Физическая культура', '10:40 - 11:20 , большой спортивный зал', 'Выполнять комплекс общеразвивающих упражнений']
5 ['Иностранный язык (английский)', '11:30 - 12:10 , 304']
6 ['История', '12:20 - 13:00 , 208', 'Изучить и подготовить устный пересказ с. 156-161, подготовить устные ответы на вопросы, заданные в тексте параграфа, научится устно объяснять даты и термины, выделенные в тексте параграфа жирным шрифтом или курсивом.']
7 ['Разговоры о важном', '13:10 - 13:50 , 207', 'Инд. задание']
8 []
9 []
    '''

    page.close()

    return diary


def get_day(date=None) -> dict:
    if date is None:
        date = str(datetime.datetime.today().strftime('%d.%m.%Y'))

    url = 'https://sgo.rso23.ru/angular/school/schedule/day/'

    page = get_page(url)
    t.sleep(1)
    data = page.find_elements(By.TAG_NAME, 'tbody')
    day_data = {}
    day_data[date] = {}
    count = 0
    for row in data:
        trs = row.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:

            if 'Уроки' in tr.text:
                continue

            count += 1
            day_data[date][count] = []

            if 'Занятие' in tr.text:
                time, subject = tr.text.split('Занятие:')
            else:
                time, subject = tr.text.split('Урок:')
            day_data[date][count].append(time.strip())
            day_data[date][count].append(subject)

    close_site(page)
    page.close()

    return day_data


def get_homework(date=None) -> dict:
    if date is None:
        date = datetime.datetime.today()
        date += datetime.timedelta(days=1)
        date = date.strftime('%d.%m.%Y')

    date = transform_date(date)

    studentdiary = get_studentdiary()

    print(studentdiary[date])

    return {date: studentdiary[date]}


def now_lesson() -> list:
    time = datetime.datetime.now().time()

    day = get_day()
    for date in day:
        for num_sub in day[date]:
            if len(day[date][num_sub]) == 0:
                continue
            time_interval = day[date][num_sub][0].replace(' ', '').split('-')
            time_end = datetime.datetime.strptime(
                time_interval[1], '%H:%M').time()

            if time_end < time:
                continue
            else:
                return day[date][num_sub]
