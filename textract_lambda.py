import boto3
import json

lambda_client = boto3.client('lambda')

def extract_text_from_s3(bucket, filename):
    payload = {"bucket": bucket, "filename": filename}
    response = lambda_client.invoke(
        FunctionName='TextractOCRHandler',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
    )
    response_payload = json.load(response['Payload'])
    if 'body' not in response_payload:
        print('Lambda response missing "body":', response_payload)
        return 'Text extraction failed: Lambda response missing "body". Full response: ' + str(response_payload)
    return json.loads(response_payload['body']).get('text', 'No text found in Lambda response.')

