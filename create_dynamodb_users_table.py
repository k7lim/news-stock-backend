import boto3

# Create a boto3 DynamoDB client
dynamodb = boto3.client('dynamodb')

# Create the users table
users_table_name = 'NewsStock_Users'

users_attribute_definitions = [
    {
        'AttributeName': 'user_id',
        'AttributeType': 'S'
    }
]

users_key_schema = [
    {
        'AttributeName': 'user_id',
        'KeyType': 'HASH'
    }
]

create_response = dynamodb.create_table(
    TableName=users_table_name,
    AttributeDefinitions=users_attribute_definitions,
    KeySchema=users_key_schema,
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
dynamodb.get_waiter('table_exists').wait(TableName=users_table_name)

# Print the response
print(create_response)