import boto3
import datetime

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb')

# Create a DynamoDB table for stock symbols
table_name = 'NewsStock_Prices'

attribute_definitions = [
    {
        'AttributeName': 'symbol',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'timestamp',
        'AttributeType': 'N'
    }
]

key_schema=[
        {
            'AttributeName': 'symbol',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'timestamp',
            'KeyType': 'RANGE'
        }
    ]

create_response = dynamodb.create_table(
    TableName=table_name,
    KeySchema=key_schema,
    AttributeDefinitions=attribute_definitions,
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
# Wait for the table to be created
dynamodb.get_waiter('table_exists').wait(TableName=table_name)

# Print the response
print(create_response)