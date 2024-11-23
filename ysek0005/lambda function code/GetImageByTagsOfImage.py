import json
import base64
import boto3
import cv2
import numpy as np
import logging
from object_detection import decode64, readbytes

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'images'  # DynamoDB table name


def lambda_handler(event, context):
    try:
        # Load the data from the event
        data = json.loads(event['body'])
        username = data.get('username')
        if not username:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: username'}),
                'headers': {
                    'Content-Type': 'application/json',
                }
            }

        image_base64 = data['file']  # Ensure the 'file' key is used for the base64 image string

        # Decode the base64 image
        img_decode = base64.b64decode(image_base64)
        img_nparray = np.frombuffer(img_decode, np.uint8)  # Correct method to convert byte string to numpy array
        img_mat = cv2.imdecode(img_nparray, cv2.IMREAD_COLOR)

        # Perform object detection
        tags = readbytes(img_decode)

        # Log the detected tags
        logger.info("Detected Tags: %s", tags)

        # Search for images in DynamoDB by tags and username
        thumbnail_urls = search_images_by_tags_and_username(tags, username)

        # Return the thumbnail URLs
        if not thumbnail_urls:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No images found matching the criteria.'}),
                'headers': {
                    'Content-Type': 'application/json',
                }
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'thumbnail_urls': thumbnail_urls}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    except Exception as e:
        logger.error("Error processing the request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }


def search_images_by_tags_and_username(tags, username):
    table = dynamodb.Table(TABLE_NAME)

    # Create filter expression for username and tags
    filter_expression = 'username = :username AND ' + ' AND '.join(
        [f"contains(tags, :tag{i})" for i in range(len(tags))])
    expression_attribute_values = {f":tag{i}": tag for i, tag in enumerate(tags)}
    expression_attribute_values[':username'] = username

    try:
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        logger.info("DynamoDB scan response: %s", response)
    except Exception as e:
        logger.error("Error scanning DynamoDB: %s", str(e))
        raise e

    items = response.get('Items', [])
    urls = [item['thumbnail_url'] for item in items]

    return urls
