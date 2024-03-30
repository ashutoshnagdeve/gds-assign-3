import json
import pandas as pd
import boto3
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=input_bucket, Key=input_key)
    body = obj['Body'].read()
    json_dicts = body.decode('utf-8').split('\r\n')

    df = pd.DataFrame(columns=['id', 'status', 'amount', 'date'])
    for line in json_dicts:
        try:
            py_dict = json.loads(line)
            if py_dict['status'] == 'delivered':
                df.loc[py_dict['id']] = py_dict
        except KeyError as e:
            print(f"KeyError: {e} in JSON dictionary")

    # Save filtered data to CSV
    df.to_csv('/tmp/test.csv', sep=',')

    # Upload CSV to S3
    date_var = str(date.today())
    try:
        file_name = f'processed_data/{date_var}_processed_data.csv'
    except:
        file_name = 'processed_data/processed_data.csv'
    bucket_name = os.getenv('output_bucket')
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    bucket.upload_file('/tmp/test.csv', file_name)

    # Send SNS notification
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn=os.getenv('TopicArn'),
        Message=f"File {input_key} has been formatted and filtered. It's been stored in {bucket_name} as {file_name}"
    )
