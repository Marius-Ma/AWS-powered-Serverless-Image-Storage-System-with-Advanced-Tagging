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
TABLE_NAME = 'fit5225A3'  # DynamoDB table name

def lambda_handler(event, context):
    try:
        # Load the data from the event
        data = json.loads(event['body'])
        image_base64 = data['file']  # Ensure the 'file' key is used for the base64 image string

        # Decode the base64 image
        img_decode = base64.b64decode(image_base64)
        img_nparray = np.frombuffer(img_decode, np.uint8)  # Correct method to convert byte string to numpy array
        img_mat = cv2.imdecode(img_nparray, cv2.IMREAD_COLOR)

        # Perform object detection
        tags = readbytes(img_decode)

        # Log the detected tags
        logger.info("Detected Tags: %s", tags)

        if not tags:
            logger.info("No tags detected for the given image.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No tags detected'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': '*'
                }
            }

        # Search for images in DynamoDB by tags
        thumbnail_urls = search_images_by_tags(tags)

        # Return the thumbnail URLs
        return {
            'statusCode': 200,
            'body': json.dumps({'thumbnail_urls': thumbnail_urls}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

    except Exception as e:
        logger.error("Error processing the request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

def search_images_by_tags(tags):
    table = dynamodb.Table(TABLE_NAME)
    filter_expression = ' AND '.join([f"contains(tags, :tag{i})" for i in range(len(tags))])
    expression_attribute_values = {f":tag{i}": tag for i, tag in enumerate(tags)}

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
