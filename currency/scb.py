import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from config import CURRENCIES, logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_info_from_page():
    response = requests.get(
        'https://www.sacombank.com.vn/company/Pages/ty-gia.aspx', verify=False)
    return response


date_str = date.today().strftime("%d/%m/%Y")


def get_record(requested_date_str):
    requested_date = datetime.strptime(requested_date_str, '%d/%m/%Y').date()
    logger.info(f'Getting SCB data for {requested_date_str}')
    res = _get_info_from_page()
    soup = BeautifulSoup(res.content, features="html.parser")
    items = soup.findAll("tr", {"class": "tr-items"})

    record = {
        "bank": "STB",
        "date": requested_date.strftime("%Y/%m/%d")
    }

    for item in items:
        currency = item.find(
            "td", {"class": "td-cell01"}).contents[1].replace(' ', '')
        if currency in CURRENCIES:
            ck = item.find("td", {"class": "td-cell04"}
                             ).contents[0].replace('.', '').replace(',', '.')
            record[currency] = float(ck)

    return record
