import json
import boto3
from botocore.exceptions import ClientError
import logging

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsStock_Users')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # parse the request body
        user = json.loads(event['body'])
        user_id = user['user_id']
        first_name = user['first_name']
        last_name = user['last_name']
        
        # check if required fields are present
        if not all([user_id, first_name, last_name]):
            raise ValueError("Missing required field(s)")

        # check if start_balance is present in the request
        start_balance = 500 # default value
        if 'start_balance' in user:
            start_balance = user['start_balance']

        # insert the new user into the users table
        response = table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression='SET first_name = :fname, last_name = :lname, balance = :balance',
            ConditionExpression='attribute_not_exists(user_id)',
            ExpressionAttributeValues={
                ':fname': first_name,
                ':lname': last_name,
                ':balance': start_balance
            },
            ReturnValues='ALL_NEW'
        )
        logger.info(response)
        # return the new user's data
        return {
            'statusCode': 200,
            'body': json.dumps({
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'balance': start_balance
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
                    'error': 'User already exists'
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
