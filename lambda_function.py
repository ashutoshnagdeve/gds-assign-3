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
        return "Event does not contain 'Records' key."

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
        df.to_csv('/tmp/test.csv',sep = ',')
        print('test.csv file created')
        date_var = str(date.today())
    try:
        file_name ='processed_data/{}_processed_data.csv'.format(date_var)
    except:
            ile_name = 'processed_data/processed_data.csv'
    lambda_path = '/tmp/test.csv'
    bucket_name = os.getenv('output_bucket')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file('/tmp/test.csv', file_name)
    
    # sns to deliver file processed request
    sns = boto3.client('sns')
    response = sns.publish( \
    TopicArn=os.getenv('TopicArn'),
    Message="File {} has been formatted and filtered. Its been stored in \
    {} as {}".format(input_key,bucket_name,file_name))