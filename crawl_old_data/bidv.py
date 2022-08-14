import pandas as pd
from time import sleep
import requests
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CURRENCIES = ['USD', 'EUR', 'JPY', 'AUD', 'HKD', 'SGD']


def _get_info_from_api(date_str: str):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://www.bidv.com.vn',
        'Referer': 'https://www.bidv.com.vn/vn/ty-gia-ngoai-te',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    data = {
        'date': date_str,
        'time': '',
    }

    return requests.post(
        'https://www.bidv.com.vn/ServicesBIDV/ExchangeDetailServlet', headers=headers, data=data)


def get_record(requested_date_str):
    requested_date = datetime.strptime(requested_date_str, '%d/%m/%Y').date()
    print(f'Getting BIDV data for {requested_date_str}')

    res = _get_info_from_api(requested_date_str)
    json_data = json.loads(res.content)

    rates = json_data['data']
    record = {
        "bank": "BIDV",
        "date": requested_date.strftime("%Y-%m-%d")
    }

    for currency in CURRENCIES:
        for rate in rates:
            if rate['currency'] == currency:
                ck = rate['ban'].replace(',', '')
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
df.to_csv('bidv_rates.csv', index=False, header=True)

print("Completed!")
