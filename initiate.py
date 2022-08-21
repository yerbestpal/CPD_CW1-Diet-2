import boto3

def create_ec2_instance(instance_type, key_name):
  # Create EC2 Instance
  ec2 = boto3.resource('ec2')
  instances = ec2.create_instances(
    # Ubuntu - ami-052efd3df9dad4825
    # ami-08e4e35cccc6189f4
    ImageId='ami-052efd3df9dad4825',
    MinCount=1,
    MaxCount=1,
    InstanceType=instance_type,
    KeyName=key_name,
    IamInstanceProfile={ 
      'Arn' : 'arn:aws:iam::973567983713:instance-profile/LabInstanceProfile'
    }
  )

  # Validate EC2 Instance
  if instances:
    print('EC2 Instance % s created' % instances[0].id)
  return

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

    # Wait until the table exists
    while table.table_status != 'ACTIVE':
      print("Waiting on successful table status")
    print("Table created successfully.")

# Create SQS Standard Queue
def create_sqs_queue(queue_name):
    sqs = boto3.resource('sqs')
    queue = sqs.create_queue(QueueName=queue_name)

    # Wait until the queue exists
    if queue.attributes.get('QueueArn'):
        print("Queue created successfully.")
    else:
        print("Queue creation failed.")

def create_sns_topic(topic_name):
  # Create SNS Topic
  sns = boto3.resource('sns')
  topic = sns.create_topic(Name=topic_name)

  # Validate SNS Topic
  if topic:
    print('SNS Topic % s created' % topic_name)
  return

create_dynamodb_table('diet2_s2030507_table')
create_sqs_queue('diet2_s2030507_queue')
# create_sns_topic('sns-s2030507')
# create_ec2_instance('t2.micro', 'vockey1')