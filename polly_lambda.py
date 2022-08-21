import json
import boto3

def lambda_handler(event, context):
  s3_client = boto3.client('s3')
  s3 = boto3.resource('s3')
  bucket = s3.Bucket('diet2-s2030507-bucket')

  for obj in bucket.objects.all():
    key = obj.key
    body = obj.get()['Body'].read()
    if event['Records'][0]['body'] == key:
      client = boto3.client('polly')
      output = client.synthesize_speech(
        OutputFormat='mp3',
        Text=body,
        TextType='text',
        VoiceId='Joanna'
      )
      # TODO - consider iterating and changing filenames with counter
      bucket.put_object(Key=key, Body=output['AudioStream'].read())