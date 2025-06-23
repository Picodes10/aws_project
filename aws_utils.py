import boto3
import uuid

# AWS credentials must be configured via environment or AWS CLI
s3 = boto3.client('s3')
bucket_name = 'access-reader'

def upload_to_s3(file, filename=None):
    if filename is None:
        filename = f"{uuid.uuid4()}.jpg"
    s3.upload_fileobj(file, bucket_name, filename)
    return filename 