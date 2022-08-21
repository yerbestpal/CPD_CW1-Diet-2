import json
import boto3

def lambda_handler(event, context):
  s3 = boto3.resource('s3')
  bucket = s3.Bucket('diet2-s2030507-bucket')

  for obj in bucket.objects.all():
    key = obj.key
    file = s3.get_object(Bucket='diet2_s2030507_bucket', Key=key)
    body = str(file['Body'].read())
    if event['Records'][0]['body'] == key:

      # Detect sentiment of text using Comprehend.
      comprehend = boto3.client('comprehend')
      sentiment = comprehend.detect_sentiment(
        Text=body,
        LanguageCode='en'
      )
      print(sentiment)

      # Save results in DynamoDB.
      if sentiment.get('Sentiment') == 'POSITIVE' or \
      sentiment.get('Sentiment') == 'NEGATIVE' or \
      sentiment.get('Sentiment') == 'MIXED':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('diet2_s2030507_table')
        table.put_item(
          Item = {
            'Image_Name': key,
            'Sentiment': sentiment
          }
        )
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
      # TODO - consider iterating and changing filenames with counter
      bucket.put_object(Key=key, Body=output['AudioStream'].read())