from base64 import b64encode
from datetime import date, datetime, timedelta
from mbb import get_record as get_mbb_record
from scb import get_record as get_scb_record
from bidv import get_record as get_bidv_record
import json
from config import logger
from utils import insert_to_dynamo, get_from_dynamo
import pandas as pd

TEMP_CSV_FILE = '/tmp/rates.csv'


def crawl(event, context):
    try:
        requested_date_str = date.today().strftime("%d/%m/%Y")
        # mbb_record = get_mbb_record(requested_date_str)
        # insert_to_dynamo(mbb_record)

        bidv_record = get_bidv_record(requested_date_str)
        insert_to_dynamo(bidv_record)

        scb_record = get_scb_record(requested_date_str)
        insert_to_dynamo(scb_record)

        logger.info("Inserted to DynamoDB")
    except Exception as e:
        logger.error(e)
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Done! Currencies data imported",
        }),
    }


def get_csv(event, context):
    try:
        end_date = date.today()
        start_date = end_date + timedelta(days=-14)

        if 'queryStringParameters' in event:
            params = event['queryStringParameters']
            if 'end_date' in params:
                end_date = datetime.strptime(
                    params['end_date'], "%d/%m/%Y").date()
            if 'start_date' in params:
                start_date = datetime.strptime(
                    params['start_date'], "%d/%m/%Y").date()

        response = get_from_dynamo(start_date, end_date)
        df = pd.DataFrame(response['Items'])
        df.to_csv(TEMP_CSV_FILE, index=False, header=True)

    except Exception as e:
        logger.error(e)
        raise e

    response = {
        "statusCode": 200,
        "headers": {
            'Content-type': 'text/csv',
            'content-disposition': 'attachment; filename=rates.csv'
        },
        "body": b64encode(open(TEMP_CSV_FILE, 'rb').read()).decode('utf-8'),
        "isBase64Encoded": True
    }
    return response
