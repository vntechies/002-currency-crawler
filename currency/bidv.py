from datetime import datetime
import requests
import json
from config import CURRENCIES, logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    logger.info(f'Getting BIDV data for {requested_date_str}')

    res = _get_info_from_api(requested_date_str)
    json_data = json.loads(res.content)

    rates = json_data['data']
    record = {
        "bank": "BIDV",
        "date": requested_date.strftime("%Y/%m/%d")
    }

    for currency in CURRENCIES:
        for rate in rates:
            if rate['currency'] == currency:
                ck = rate['ban'].replace(',', '')
                record[currency] = float(ck)

    return record
