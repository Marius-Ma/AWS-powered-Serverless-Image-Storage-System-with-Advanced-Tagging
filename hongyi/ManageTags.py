import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: %s", event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('fit5225A3')  # Your table name
    results = []  # List to store results of operations

    try:
        body = json.loads(event['body'])
        urls = body.get('url', [])
        tags = body.get('tags', [])
        operation_type = body.get('type')
        logger.info("URLs: %s, Tags: %s, Operation type: %s", urls, tags, operation_type)
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

    if not urls or not tags or operation_type not in [0, 1]:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input parameters'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

    for url in urls:
        response = table.scan(
            FilterExpression="thumbnail_url = :url",
            ExpressionAttributeValues={":url": url}
        )
        items = response.get('Items', [])
        if not items:
            logger.warning("No items found for URL: %s", url)
            results.append({'url': url, 'status': 'URL not found'})
            continue

        item = items[0]
        current_tags = item.get('tags', [])

        if operation_type == 1:
            updated_tags = current_tags + tags
        else:
            updated_tags = current_tags[:]
            for tag in tags:
                if tag in updated_tags:
                    updated_tags.remove(tag)

        table.update_item(
            Key={'username': item['username'], 'key': item['key']},
            UpdateExpression="SET tags = :tags",
            ExpressionAttributeValues={":tags": updated_tags}
        )
        results.append({'url': url, 'status': 'Tags updated'})

    return {
        'statusCode': 200,
        'body': json.dumps({'results': results}),
        'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
        }
    }
