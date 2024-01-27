# Импорт необходимых библиотек
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


import time as t
import datetime

import os


from dotenv import load_dotenv

# Сдесь хранятся дни недели,
# которые нужны для форматирования текста
WEEKDAYS = ['Понедельник',
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"]


# В этой функции мы переобразовываем дату date
# из типа datetime модуля datetime в строку.
def transform_date(date: datetime) -> str:
    # список с месяцами
    # он нужен чтобы перевести номер месяца в его название
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

    # разбиваем дату date на день, месяц и год
    day, month, year = date.split('.')
    # формируем объект типа datetime чтобы получить
    # порядковый номер недели
    a = datetime.datetime(int(year),
                          int(month),
                          int(day))
    # по порядковому номеру находим название дня недели
    week_day = WEEKDAYS[a.weekday()]

    # формируем нужную нам строку и возвращаем ее
    return f'{week_day}, {day} {months[int(month) - 1]} {year} г.'


# в этой функции проверяется существование
# пути до определенного html элемента,
# который содержит в себе текст
def check_exists_by_xpath(driver, xpath):
    try:
        # пытаемся получить путь
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        # если возникает ошибка, то пути нет
        # и поэтому возвращаем False
        return False
    # если ошибки не возникло, то путь
    # существует
    return True


# Проверка существования тэга html
def check_exists_by_tag(driver, tag):
    try:
        driver.find_element(By.TAG_NAME, tag)
    except NoSuchElementException:
        return False
    return True


# Функция выхода из учетной записи sgo.rso23.ru
def close_site(page: webdriver.Chrome) -> None:

    if check_exists_by_xpath(page, "//*[contains(text(), 'Выход')]"):
        # если есть нужные нам кнопки, то нажимаем их и выходим
        page.find_element(
            By.XPATH, "//*[contains(text(), 'Выход')]").click()
        t.sleep(0.2)
        page.find_element(
            By.XPATH, "//*[contains(text(), 'Да')]").click()


# функция проверки существования
# html элемента с определенным классом
def check_exists_by_classname(driver, name):
    try:
        driver.find_element(By.CLASS_NAME, name)
    except NoSuchElementException:
        return False
    return True


# Фунция загрузки страницы
# принимает ссылку на любую страницу
# домена sgo.rso23.ru
def get_page(url) -> webdriver.Chrome:
    # загружаем данные для входа
    load_dotenv('.env')

    # создаем браузер
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome()

    # открываем страницу
    browser.get(url)
    # ждем 2 сек
    t.sleep(2)

    # далее находим элементы и нажимаем на кнопки,
    # переодически ожидая
    browser.find_element(By.CLASS_NAME, "select2-selection__arrow").click()

    t.sleep(0.5)
    browser.find_element(
        By.CLASS_NAME, "select2-search__field").send_keys(os.getenv('SGORSO_SCHOOL'))
    t.sleep(0.5)
    browser.find_element(By.CLASS_NAME, "select2-results__option").click()
    t.sleep(0.5)
    browser.find_element(By.NAME, 'loginname').send_keys(
        os.getenv('SGORSO_LOGIN'))
    t.sleep(0.5)
    browser.find_element(By.NAME, 'password').send_keys(
        os.getenv('SGORSO_PASS'))
    t.sleep(0.5)
    browser.find_element(By.CLASS_NAME, "primary-button").click()
    t.sleep(0.5)
    if check_exists_by_xpath(browser, "//*[contains(text(), 'Продолжить')]"):
        browser.find_element(
            By.XPATH, "//*[contains(text(), 'Продолжить')]").click()
    t.sleep(2)

    # когда мы оказались на нужной странице
    # уже в нашем аккауне, возвращаем
    # страницу
    return browser


# функция получения данных на неделю
def get_studentdiary() -> dict:
    # ссылка на страницу
    url = 'https://sgo.rso23.ru/angular/school/studentdiary/'

    # получаем данные со страницы
    page = get_page(url)
    t.sleep(3)
    # получить сегодняшний день недели
    date = datetime.datetime.today()
    week_day = date.weekday()
    # Если сегодня или завтра воскресенье,
    # то нужно изменить алгоритм получения данных
    if week_day == 6 or week_day + 1 == 6:
        page.find_element(By.CLASS_NAME, "button_next").click()
        t.sleep(3)

    # далее происходит сложные переборы
    # и поиски нужной информации (мне лень объяснять)
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
    # завершаем сессию
    close_site(page)
    page.close()

    # возвращаем полученные данные со страницы
    return diary
