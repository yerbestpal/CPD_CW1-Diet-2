import boto3

# Create DynamoDB table
def create_dynamodb_table(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'Image_Name',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Image_Name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Table status:", table.table_status)

    while table.table_status != 'ACTIVE':
      print("Waiting on successful table status")
    print("Table created successfully.")

# Create SQS Standard Queue
def create_sqs_queue(queue_name):
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName=queue_name)

    if queue.attributes.get('QueueArn'):
        print("Queue created successfully.")
    else:
        print("Queue creation failed.")

create_dynamodb_table('diet2_s2030507_table')
create_sqs_queue('diet2_s2030507_queue')