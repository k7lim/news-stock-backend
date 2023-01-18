import json
import boto3
import requests
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('NewsStock_Prices')

def lambda_handler(event, context):
    # Retrieve all unique symbols from the table
    response = table.scan()
    symbols = set([item['symbol'] for item in response['Items']])
    
    for symbol in symbols:
        url = f'https://newsapi.org/v2/everything?q={symbol}&sortBy=popularity&apiKey=6148f21872644a2bb5b89d2978c22ac5'
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Invalid response from newsapi")
        price = response.json()['totalResults']
        timestamp = int(time.time())
        response = table.put_item(
            Item={
                'symbol': {'S': symbol},
                'timestamp': {'N': timestamp},
                'price': {'N': price}
            }
        )
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Prices updated successfully'
        })
    }
