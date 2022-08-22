import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from config import CURRENCIES, logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _init_request():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    return requests.get(
        'https://www.mbbank.com.vn/ExchangeRate', headers=headers, verify=False)


def _get_info_from_api(date: str, cookies: dict, xsrf_token: str):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'MB-XSRF-Token-FormOnline': xsrf_token,
        'Referer': 'https://www.mbbank.com.vn/ExchangeRate',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    return requests.get(
        f'https://www.mbbank.com.vn/api/getExchangeRate/{date}', headers=headers, cookies=cookies, verify=False)


def get_record(requested_date_str):
    logger.info(f'Getting MBB data for {requested_date_str}')

    requested_date = datetime.strptime(requested_date_str, '%d/%m/%Y').date()
    date_str_param = requested_date.strftime("%Y-%m-%d")

    init_res = _init_request()
    soup = BeautifulSoup(init_res.content, features="html.parser")
    xsrf_token = soup.find(
        'input', {'name': '__RequestVerificationToken'}).get('value')

    currency_rate_res = _get_info_from_api(
        date_str_param, init_res.cookies.get_dict(), xsrf_token)
    json_data = json.loads(currency_rate_res.content)
    rates = json_data['lst']

    record = {
        "bank": "MBB",
        "date": requested_date.strftime("%Y/%m/%d")
    }

    for currency in CURRENCIES:
        for rate in rates:
            if rate['currencyCode'] == currency:
                ck = f"{rate['sell_bank_transfer']}"
                record[currency] = float(ck)

    return record
