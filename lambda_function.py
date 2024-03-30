import json
import pandas as pd
import boto3
import io
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    # Check if 'Records' key exists in the event object
    if 'Records' not in event:
        print("Event does not contain 'Records' key.")
        return

    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']
    if input_bucket != 's3-doordash-landing' or 'raw_data/' not in input_key:
        return

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=input_bucket, Key=input_key)
    body = obj['Body'].read()
    # Assuming the JSON data is separated by '\r\n', adjust if necessary
    json_dicts = body.decode('utf-8').split('\r\n')

    df = pd.DataFrame(columns=['id', 'status', 'amount', 'date'])
    for line in json_dicts:
        try:
            py_dict = json.loads(line)
            if py_dict.get('status') == 'delivered':
                df.loc[py_dict['id']] = py_dict
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            continue

    df.to_csv('/tmp/test.csv', sep=',')
    print('test.csv file created')

    date_var = str(date.today())
    file_name = f'processed_data/{date_var}_processed_data.csv'

    bucket_name = os.getenv('output_bucket')
    s3 = boto3.resource('s3')
    s3.meta.client.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': 's3-doordash-landing', 'Key': input_key},
        Key=file_name
    )
    print(f'File copied to S3://{bucket_name}/{file_name}')
