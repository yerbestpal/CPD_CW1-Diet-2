import json
import boto3
import re
from decimal import Decimal

def lambda_handler(event, context):
  s3_client = boto3.client('s3')
  s3_resource = boto3.resource('s3')
  bucket = s3_resource.Bucket('diet2-s2030507-bucket')

  sentiment = 0

  # Loop through S3 objects.
  for obj in bucket.objects.all():
    key = obj.key
    print("obj key: " + key)
    json_string = json.loads(event['Records'][0]['body'])
    file_name = str(json_string['Records'][0]['s3']['object']['key'])
    print("Records: " + file_name)
    file = s3_client.get_object(Bucket='diet2-s2030507-bucket', Key=key)
    body = str(file['Body'].read())
    print("body: " + body)

    print("FILE: " + str(file))

    if file_name == key:
      if key[key.rfind('.') + 1:len(key)] == 'txt':
        # Detect sentiment of text using Comprehend.
        comprehend = boto3.client('comprehend')
        sentiment = comprehend.detect_sentiment(
          Text=body,
          LanguageCode='en'
        )
        print(sentiment.get('Sentiment'))

        # Save results in DynamoDB.
        if sentiment.get('Sentiment') == 'POSITIVE' or \
        sentiment.get('Sentiment') == 'NEGATIVE' or \
        sentiment.get('Sentiment') == 'MIXED':
          dynamodb = boto3.resource('dynamodb')
          table = dynamodb.Table('diet2_s2030507_table')
          item = json.loads(json.dumps({
            'Image_Name': key,
            'Sentiment': sentiment
          }), parse_float=Decimal)
          table.put_item(Item=item)
          print('Saved sentiment in DynamoDB.')

          # Send notification of NEGATIVE sentiment to SNS
          if sentiment.get('Sentiment') == 'NEGATIVE':
            sns = boto3.client('sns')
            sns.publish(
              TopicArn='arn:aws:sns:us-east-1:973567983713:diet2-s2030507-sns',
              Message=json.dumps({'default': json.dumps(sentiment)}),
              Subject='File upload status'
            )
            print('Sent notification to SNS.')

        # Convert text to speech using Polly.
        client = boto3.client('polly')
        output = client.synthesize_speech(
          OutputFormat='mp3',
          Text=body,
          TextType='text',
          VoiceId='Joanna'
        )

        # Extract file number from key name and concatenate into audio file name.
        number = re.findall(r'\d', key)
        bucket.put_object(Key="audio_files/audio" + str(number[0]) + ".mp3", Body=output['AudioStream'].read())

  return {
    'statusCode': 200,
    'body': sentiment
  }