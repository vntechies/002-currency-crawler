import boto3
from config import logger
from datetime import datetime
from boto3.dynamodb.conditions import Key

TABLE_NAME = 'Currency'
REGION_NAME = 'ap-southeast-1'

dynamodb_config = {
    'region_name': REGION_NAME
}
dynamodb = boto3.resource('dynamodb', **dynamodb_config)
table = dynamodb.Table(TABLE_NAME)


def insert_to_dynamo(record):
    try:
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')

        record
        record['dt'] = now_str

        table.put_item(Item=record)

    except Exception as e:
        logger.error(e)
        raise e

    return True


def get_from_dynamo(start_date, end_date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    filter_expression = Key('date').between(start_date_str, end_date_str)

    response = table.scan(
        FilterExpression=filter_expression
    )
    return response
