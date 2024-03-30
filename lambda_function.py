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

    # Define the S3 bucket and object name for the CSV file
    bucket_name = os.getenv('output_bucket')
    object_name = 'processed_data/processed_data.csv'

    # Download the existing CSV file from S3
    s3.download_file(bucket_name, object_name, '/tmp/processed_data.csv')

    # Read the existing CSV file into a DataFrame
    existing_df = pd.read_csv('/tmp/processed_data.csv')

    # Append the new records to the existing DataFrame
    appended_df = pd.concat([existing_df, df], ignore_index=True)

    # Write the updated DataFrame back to the CSV file
    appended_df.to_csv('/tmp/processed_data.csv', index=False)

    # Upload the updated CSV file back to S3
    s3.upload_file('/tmp/processed_data.csv', bucket_name, object_name)

    print('Records appended to the CSV file and uploaded to S3')

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully appended records to CSV and uploaded to S3')
    }
