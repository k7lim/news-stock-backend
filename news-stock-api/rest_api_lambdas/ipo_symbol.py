import json
import boto3
from botocore.exceptions import ClientError
import logging
import requests
import time
import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsStock_Prices')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # parse the request body
        body = json.loads(event['body'])
        user_id = body['user_id']
        symbol = body['symbol']
        
        # check if required fields are present
        if not all([user_id, symbol]):
            raise ValueError("Missing required field(s)")

        # Check if the symbol already exists in the table
        response = table.get_item(
            Key={
                'symbol': {'S': symbol}
            }
        )
        
        # If the symbol already exists, return an error
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Symbol already exists'
                })
            }
        
        # If the symbol does not exist, insert it into the table
        else:
            now = datetime.datetime.now()
            from_iso = (now - datetime.timedelta(hours=24)).isoformat()

            url = f'https://newsapi.org/v2/everything?q={symbol}&from={from_iso}&sortBy=popularity&apiKey=6148f21872644a2bb5b89d2978c22ac5'
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError("Invalid response from newsapi")
            price = response.json()['totalResults']
            if price <= 0:
                raise ValueError("no results for that term, can't IPO a 0 value symbol")
            timestamp = int(time.time())
            response = table.put_item(
                Item={
                    'symbol': {'S': symbol},
                    'timestamp': {'N': timestamp},
                    'price': {'N': price},
                    'ipo_user_id': {'S': user_id}
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Symbol added successfully'
                })
            }
    except ValueError as e:
        logger.error("ValueError occurred: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Missing required field(s)"
            })
        }
    except KeyError as e:
        logger.error("KeyError occurred: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Missing required field(s)"
            })
        }
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Symbol already exists'
                })
            }
    except Exception as e:
        print("Type of exception:", type(e))
        logger.error(f"Error occured while creating user: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
