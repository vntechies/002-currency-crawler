from datetime import date
from mbb import get_record as get_mbb_record
from scb import get_record as get_scb_record
from bidv import get_record as get_bidv_record
import json
from config import logger
from utils import append_to_db, format_record

def crawl(event, context):
    try:
        requested_date_str = date.today().strftime("%d/%m/%Y")
        # mbb_record = get_mbb_record(requested_date_str)
        # append_to_db(format_record(mbb_record))
        
        bidv_record = get_bidv_record(requested_date_str)
        append_to_db(format_record(bidv_record))

        scb_record = get_scb_record(requested_date_str)
        append_to_db(format_record(scb_record))

        logger.info("Inserted to Google sheet")
    except Exception as e:
        logger.error(e)
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Done! Currencies data imported",
        }),
    }
