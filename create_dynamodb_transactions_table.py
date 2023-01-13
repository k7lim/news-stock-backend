import boto3

# Create a boto3 DynamoDB client
dynamodb = boto3.client('dynamodb')

# Create the transactions table
transactions_table_name = 'NewsStock_Transactions'

transactions_attribute_definitions = [
    {
        'AttributeName': 'transaction_id',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'timestamp',
        'AttributeType': 'N'
    }
]

transactions_key_schema = [
    {
        'AttributeName': 'transaction_id',
        'KeyType': 'HASH'
    },
    {
        'AttributeName': 'timestamp',
        'KeyType': 'RANGE'
    }
]

create_response = dynamodb.create_table(
    TableName=transactions_table_name,
    AttributeDefinitions=transactions_attribute_definitions,
    KeySchema=transactions_key_schema,
        ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
dynamodb.get_waiter('table_exists').wait(TableName=transactions_table_name)

# Print the response
print(create_response)