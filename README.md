DoorDash Data Pipeline README

Overview

This repository contains the code and configuration files for setting up a data pipeline to process DoorDash daily data.

Steps to Create and Deploy

  1. JSON File Creation

- Create a JSON file from the provided sample JSON data.

  2. S3 Bucket Creation

- Create two S3 buckets:
  1. **s3-doordash-landing:** Store packages from CodeBuild in zip form and insert DoorDash daily data in the `raw_data` folder.
  2. **s3-doordash-filtered:** Store filtered data containing records with a "delivered" status.

  3. Code and Dependencies Setup

- Create a repository in GitHub and clone it to your local machine.
- Add the following files to your repository:
  - `lambda_function.py`: Contains Lambda code.
  - `buildspec.yml`: Defines the build steps in CodeBuild (in the test branch initially, then merge with the main branch).
- Set up a virtual environment using CodeBuild.
- Package the Lambda function along with `.env` and `.json` files, and upload it to S3.
- Create a `requirements.txt` file containing dependencies to be installed.

  4. CodeBuild Project Creation

- Create a CodeBuild project with GitHub as the source and select the repository containing the code, dependencies, and `buildspec.yml`.
- Add a webhook for `pull_request_merged` events to trigger the CodeBuild project automatically.

  5. Lambda Function Creation

- Create a Lambda function named `doordash_transform`.
- Assign SNS and S3 full access permissions to the Lambda role.
- Add the Lambda code via the buildspec command.
- Add the `python_dotenv` layer to the Lambda function.
- Manually create a test event and execute the Lambda code to ensure it works correctly.
- Verify that the transformed CSV is stored in `s3-doordash-target` bucket.

Challenges Faced

1. **Access Denied Error:** Initially faced issues with permissions while moving the deployment package to S3. Resolved by adding specific bucket permissions to the CodeBuild IAM role.
2. **Layer Addition:** Encountered difficulties adding layers using buildspec commands; ended up adding the layer manually.
3. **Exception Handling:** Dealt with multiple exceptions while executing the Lambda code, but successfully achieved the desired output in the destination folder in the `s3-doordash-target` bucket.

