import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_tags(tag_list):
    tag_counts = {}
    for tag in tag_list:
        try:
            tag, count = tag.rsplit(',', 1)
            tag = tag.strip('" ')
            count = int(count.strip())
            tag_counts[tag] = count
        except ValueError as e:
            logger.error("Error parsing tag: %s", tag)
            raise ValueError(f"Invalid tag format: {tag}")
    return tag_counts

def lambda_handler(event, context):
    logger.info("Event: %s", event)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images')  # your table name

    # Validation: Check if body is provided
    if 'body' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing request body'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    body = json.loads(event['body'])

    if 'username' not in body or 'tags' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields: username and tags'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    username = body['username']
    tags = body['tags']

    try:
        tag_counts = parse_tags(tags)
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    # Scan the table and filter results by username
    try:
        response = table.scan(
            FilterExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        logger.info("DynamoDB scan response: %s", response)
    except Exception as e:
        logger.error("Error scanning DynamoDB: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error scanning DynamoDB', 'message': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    items = response.get('Items', [])
    filtered_items = []
    for item in items:
        item_tags = item.get('tags', [])
        if not isinstance(item_tags, list):
            logger.error("Tags field is not a list: %s", item_tags)
            continue

        tag_count_map = {}
        for tag in item_tags:
            if isinstance(tag, str):
                if tag in tag_count_map:
                    tag_count_map[tag] += 1
                else:
                    tag_count_map[tag] = 1
            else:
                logger.error("Unexpected tag format: %s", tag)

        # Check if item meets the tag count criteria
        meets_criteria = all(tag_count_map.get(tag, 0) >= count for tag, count in tag_counts.items())
        if meets_criteria:
            filtered_items.append(item)

    urls = [item['thumbnail_url'] for item in filtered_items if 'thumbnail_url' in item]

    if not urls:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'No images found matching the criteria.'}),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'links': urls}),
        'headers': {
            'Content-Type': 'application/json',
        }
    }
