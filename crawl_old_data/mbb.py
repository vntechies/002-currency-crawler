import pandas as pd
from time import sleep
import requests
import json
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from decimal import Decimal
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CURRENCIES = ['USD', 'EUR', 'JPY', 'AUD', 'HKD', 'SGD']


def _init_request():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'ASP.NET_SessionId=tqa2yya1v21crn4i3qy3brnd; __RequestVerificationToken=RTDcbBT0489ThjzKSfrcKn6V2w_-a8WvMOSVRc7m0UJhk8JMNNJaIs83p04w8J6oDlrPnuUw_lnpf3aDzSyJvfRVrvGURPOZp_Op0c9dzyc1; _fbp=fb.2.1660238327199.1286053738; alias_current=',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
    }

    return requests.get(
        'https://www.mbbank.com.vn/ExchangeRate', headers=headers, verify=False)


def _get_info_from_api(date: str, cookies: dict, xsrf_token: str):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'ASP.NET_SessionId=tqa2yya1v21crn4i3qy3brnd; __RequestVerificationToken=RTDcbBT0489ThjzKSfrcKn6V2w_-a8WvMOSVRc7m0UJhk8JMNNJaIs83p04w8J6oDlrPnuUw_lnpf3aDzSyJvfRVrvGURPOZp_Op0c9dzyc1; _fbp=fb.2.1660238327199.1286053738; alias_current=',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
        'MB-XSRF-Token-FormOnline': xsrf_token,
        'Referer': 'https://www.mbbank.com.vn/ExchangeRate',
    }

    return requests.get(
        f'https://www.mbbank.com.vn/api/getExchangeRate/{date}', headers=headers, cookies=cookies, verify=False)


def get_record(requested_date_str):
    print(f'Getting MBB data for {requested_date_str}')

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
        "date": requested_date.strftime("%Y-%m-%d")
    }

    for currency in CURRENCIES:
        for rate in rates:
            if rate['currencyCode'] == currency:
                ck = f"{rate['sell_bank_transfer']}"
                record[currency] = Decimal(ck)

    return record


end_date = date.today()
current_date = end_date + timedelta(days=-150)
delta = timedelta(days=1)

docs = []

while current_date <= end_date:
    if current_date.weekday() > 4:
        print("Skip weekends")
        current_date += delta
        continue
    current_date_str = current_date.strftime("%d/%m/%Y")
    print(f"getting data for date {current_date_str}")
    docs.append(get_record(current_date_str))
    current_date_str
    current_date += delta
    sleep(2)
df = pd.DataFrame(docs)
df.to_csv('mbb_rates.csv', index=False, header=True)

print("Completed!")
