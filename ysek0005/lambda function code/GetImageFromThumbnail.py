import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: %s", event)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images')  # your table name

    # Validation: Check if query parameters are provided
    if 'queryStringParameters' not in event or 'thumbnail_url' not in event['queryStringParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required query parameter: thumbnail_url'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    thumbnail_url = event['queryStringParameters']['thumbnail_url']

    # Validation: Ensure the thumbnail URL is not empty
    if not thumbnail_url.strip():
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid thumbnail_url parameter. It should be a non-empty string.'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    try:
        response = table.scan(
            FilterExpression="thumbnail_url = :url",
            ExpressionAttributeValues={":url": thumbnail_url}
        )
        logger.info("DynamoDB scan response: %s", response)
    except Exception as e:
        # Error handling: Return 500 if there is an internal server error
        logger.error("Error scanning DynamoDB: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'message': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    items = response.get('Items', [])

    # Validation: Ensure the thumbnail URL exists in the database
    if not items:
        logger.warning("Thumbnail URL not found: %s", thumbnail_url)
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Thumbnail URL not found'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    full_size_url = items[0].get('image_url', 'URL not found')

    return {
        'statusCode': 200,
        'body': json.dumps({'fullSizeUrl': full_size_url}),
        'headers': {
            'Content-Type': 'application/json',
        }
    }
