import json
import boto3
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the bucket name as a variable for reusability
bucket_name = 'fit5225a3group87'  # your bucket name

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('fit5225A3')  # your table name
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    logger.info("Event: %s", event)

    try:
        body = json.loads(event['body'])
        urls = body.get('urls', [])
        logger.info("URLs to delete: %s", urls)
    except Exception as e:
        logger.error("Error parsing request body: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body', 'message': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

    if not urls:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No URLs provided to delete'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

    for url in urls:
        try:
            pattern = r'/thumbnails(/.*)'

            # Extract path after /thumbnails
            match = re.search(pattern, url)

            if match:
                path = match.group(1)

                # Extract username
                user_name_pattern = r'([^/]+)/'
                user_name_match = re.search(user_name_pattern, path)

                if user_name_match:
                    user_name = user_name_match.group(1)

            response = table.get_item(
                Key={
                    'username': user_name,
                    'key': 'images' + path
                }
            )
            logger.info("DynamoDB get_item response: %s", response)
            # logger.info("DynamoDB scan response: %s", response)
        except Exception as e:
            logger.error("Error scanning DynamoDB: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error scanning DynamoDB', 'message': str(e)}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': '*'
                }
            }

        item = response['Item']
        if not item:
            logger.warning("No item found for URL: %s", url)
            continue

        try:
            # Delete from S3
            logger.info("Deleting from S3: %s and %s ", item['thumbnail_url'], item['image_url'])
            delete_object_from_url(item['thumbnail_url'])
            delete_object_from_url(item['image_url'])

            # Delete from DynamoDB
            logger.info("Deleting from DynamoDB: %s, %s", item['username'], item['key'])
            table.delete_item(Key={'username': item['username'], 'key': item['key']})
        except Exception as e:
            logger.error("Error deleting item: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error', 'message': str(e)}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': '*'
                }
            }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Images deleted successfully'}),
        'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
        }
    }


def delete_object_from_url(s3_url):
    match = re.match(r'https://(.+?)\.s3\.amazonaws\.com/(.+)', s3_url)
    if not match:
        raise ValueError("Invalid S3 URL")

    bucket_name = match.group(1)
    object_key = match.group(2)

    response = s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    return response
