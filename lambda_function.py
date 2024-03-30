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
    body = obj['Body'].read().decode('utf-8')

    # Split the body into lines and process each line as JSON
    json_dicts = body.split('\n')
    filtered_data = []
    for line in json_dicts:
        try:
            json_data = json.loads(line)
            if json_data.get('status') == 'delivered':  # Check 'status' field
                filtered_data.append(json_data)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from line: {line}")

    # Create a DataFrame from the filtered data
    df = pd.DataFrame(filtered_data)

    if df.empty:
        return "No data with status 'delivered' found."

    # Generate a unique filename based on the current date
    date_var = str(date.today())
    file_name = f'processed_data/{date_var}_processed_data.csv'

    # Write the DataFrame to a CSV file in the Lambda's /tmp directory
    df.to_csv('/tmp/test.csv', index=False)

    # Upload the CSV file to the target S3 bucket
    target_bucket_name = os.getenv('output_bucket')
    s3_target = boto3.resource('s3')
    bucket_target = s3_target.Bucket(target_bucket_name)
    bucket_target.upload_file('/tmp/test.csv', file_name)

    # Notify using SNS
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=os.getenv('TopicArn'),
        Message=f"File {input_key} has been formatted and filtered. It's been stored in {target_bucket_name} as {file_name}"
    )

    return "Processing completed successfully."
