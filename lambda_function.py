import json
import pandas as pd
import boto3
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

def lambda_handler(event, context):
    # Check if 'Records' key exists in the event object
    if 'Records' not in event:
        print("Event does not contain 'Records' key.")
        return

    # Assuming there's only one record in the list
    record = event['Records'][0]

    # Extract necessary information from the record
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']

    # Verify if the object is in the correct folder
    if not object_key.startswith('raw_data/'):
        print("Object is not in the 'raw_data' folder.")
        return

    # Get the S3 object
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=object_key)
    body = obj['Body'].read().decode('utf-8')

    # Load JSON data from S3
    try:
        json_data = json.loads(body)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return

    # Filter records with status 'delivered'
    filtered_data = [record for record in json_data if record.get('status') == 'delivered']

    if not filtered_data:
        print("No data with status 'delivered' found.")
        return

    # Create a DataFrame from the filtered data
    df = pd.DataFrame(filtered_data)

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
        Message=f"File {object_key} has been formatted and filtered. It's been stored in {target_bucket_name} as {file_name}"
    )

    return "Processing completed successfully."
