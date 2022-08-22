from decimal import Decimal
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import pandas as pd

import pdb
CURRENCIES = ['USD', 'EUR', 'JPY', 'AUD', 'HKD', 'SGD']


def get_record(requested_date_str, driver):
    driver.find_element(By.CSS_SELECTOR, "#dtpNgayMoney > span > i").click()
    title = driver.find_element(
        By.CSS_SELECTOR, "ul > li > div > div > table > thead> tr > th:nth-child(2)")
    previous_button = driver.find_element(
        By.CSS_SELECTOR, "ul > li > div > div > table > thead> tr > th:nth-child(1)")
    next_button = driver.find_element(
        By.CSS_SELECTOR, "ul > li > div > div > table > thead> tr > th:nth-child(3)")
    current_month = int(title.text.split(' ')[1])
    requested_date = datetime.strptime(requested_date_str, '%d/%m/%Y').date()
    while requested_date.month < current_month:
        previous_button.click()
        current_month = int(title.text.split(' ')[1])
    while requested_date.month > current_month:
        next_button.click()
        current_month = int(title.text.split(' ')[1])
    cal_body = driver.find_element(
        By.CSS_SELECTOR, "div.datepicker-days > table > tbody")
    cal_body.find_element(
        By.XPATH, f"//td[text()='{requested_date.day}']").click()
    sleep(randint(10,20))
    delay = 3  # seconds
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#bdUSDG7 > table')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")
    table = driver.find_element(By.CSS_SELECTOR, "#bdUSDG7 > table")
    content = table.get_attribute('innerHTML')
    soup = BeautifulSoup(content, features="html.parser")
    items = soup.findAll("tr", {"class": "tr-items"})
    record = {
        "bank": "STB",
        "date": requested_date.strftime("%Y-%m-%d")
    }
    for item in items:
        currency = item.find(
            "td", {"class": "td-cell01"}).contents[1].replace(' ', '')
        if currency in CURRENCIES:
            rate = item.find("td", {"class": "td-cell04"}
                             ).contents[0].replace('.', '').replace(',', '.')
            record[currency] = Decimal(rate)
    table = driver.find_element(By.CSS_SELECTOR, "#bdOther > table")

    content = table.get_attribute('innerHTML')
    soup = BeautifulSoup(content, features="html.parser")
    items = soup.findAll("tr", {"class": "tr-items"})
    for item in items:
        currency = item.find(
            "td", {"class": "td-cell01"}).contents[1].replace(' ', '')
        if currency in CURRENCIES:
            rate = item.find("td", {"class": "td-cell04"}
                             ).contents[0].replace('.', '').replace(',', '.')
            record[currency] = Decimal(rate)
    return record


end_date = date.today()
current_date = end_date + timedelta(days=-150)
delta = timedelta(days=1)

docs = []
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.sacombank.com.vn/company/Pages/ty-gia.aspx")

while current_date <= end_date:
    if current_date.weekday() > 4:
        print("Skip weekends")
        current_date += delta
        continue
    current_date_str = current_date.strftime("%d/%m/%Y")
    print(f"getting data for date {current_date_str}")
    docs.append(get_record(current_date_str, driver))
    current_date_str
    current_date += delta
    sleep(2)
df = pd.DataFrame(docs)
df.to_csv('scb_rates.csv', index=False, header=True)

print("Completed!")
