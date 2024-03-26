import json
import pandas as pd
import boto3
import io
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    # Code to read JSON data from S3, process it, and upload the processed data
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=input_bucket, Key=input_key)
    body = obj['Body'].read()
    json_dicts = body.decode('utf-8').split('\r\n')
    
    df = pd.DataFrame(columns=['id', 'status', 'amount', 'date'])
    for line in json_dicts:
        py_dict = json.loads(line)
        if py_dict['status'] == 'delivered':
            df.loc[py_dict['id']] = py_dict
    
    df.to_csv('/tmp/test.csv', sep=',')
    print('test.csv file created')

    date_var = str(date.today())
    file_name = f'processed_data/{date_var}_processed_data.csv'  # Using format method

    # Upload the processed CSV file to the output S3 bucket
    bucket_name = os.getenv('output_bucket')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file('/tmp/test.csv', file_name)
    print(f'File uploaded to S3://{bucket_name}/{file_name}')

    # Publish a message to the SNS topic
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=os.getenv('TopicArn'),
        Message=f"File {input_key} has been formatted and filtered. It's been stored in {bucket_name} as {file_name}"
    )
    print('Notification sent to SNS topic')
