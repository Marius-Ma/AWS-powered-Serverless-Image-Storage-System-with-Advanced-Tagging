import json
import boto3
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the bucket name as a variable for reusability
bucket_name = 'fit5225a3group87'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('fit5225A3')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    all_images_found = True
    errors = []

    logger.info("Event: %s", event)

    try:
        body = json.loads(event['body'])
        urls = body.get('urls', [])
        logger.info("URLs to delete: %s", urls)
    except Exception as e:
        logger.error("Error parsing request body: %s", str(e))
        return create_response(400, 'Invalid request body', str(e))

    if not urls:
        return create_response(400, 'No URLs provided to delete')

    for url in urls:
        if not process_url(url, errors):
            all_images_found = False

    if not all_images_found:
        return create_response(200, 'Images not found', errors)

    for url in urls:
        delete_images(url, errors)

    if errors:
        return create_response(400, 'Some errors occurred', errors)

    return create_response(200, 'Images deleted successfully')


def process_url(url, errors):
    try:
        path, user_name = extract_path_and_username(url)
        response = table.get_item(Key={'username': user_name, 'key': 'images' + path})
        logger.info("DynamoDB get_item response: %s", response)
    except Exception as e:
        logger.error("Error scanning DynamoDB: %s", str(e))
        errors.append({'url': url, 'message': 'Error scanning DynamoDB', 'error': str(e)})
        return False

    item = response.get('Item')
    if not item:
        logger.warning("Images not found: %s", url)
        errors.append({'url': url, 'message': 'Images not found'})
        return False

    return True


def delete_images(url, errors):
    try:
        path, user_name = extract_path_and_username(url)
        response = table.get_item(Key={'username': user_name, 'key': 'images' + path})
        item = response.get('Item')
        if not item:
            return

        logger.info("Deleting from S3: %s and %s", item['thumbnail_url'], item['image_url'])
        delete_object_from_url(item['thumbnail_url'])
        delete_object_from_url(item['image_url'])

        logger.info("Deleting from DynamoDB: %s, %s", item['username'], item['key'])
        table.delete_item(Key={'username': item['username'], 'key': item['key']})
    except Exception as e:
        logger.error("Error deleting item: %s", str(e))
        errors.append({'url': url, 'message': 'Error deleting item', 'error': str(e)})


def extract_path_and_username(url):
    pattern = r'/thumbnails(/.*)'
    match = re.search(pattern, url)
    if match:
        path = match.group(1)
        user_name_pattern = r'([^/]+)/'
        user_name_match = re.search(user_name_pattern, path)
        if user_name_match:
            user_name = user_name_match.group(1)
            return path, user_name
    raise ValueError("Invalid URL format")


def delete_object_from_url(s3_url):
    match = re.match(r'https://(.+?)\.s3\.amazonaws\.com/(.+)', s3_url)
    if not match:
        raise ValueError("Invalid S3 URL")

    bucket_name = match.group(1)
    object_key = match.group(2)

    s3_client.delete_object(Bucket=bucket_name, Key=object_key)


def create_response(status_code, message, errors=None):
    body = {'message': message}
    if errors:
        body['errors'] = errors
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        }
    }
