import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
TOPIC_ARN = "arn:aws:sns:us-east-1:966781677907:fit5225a3"
TABLE_NAME = 'fit5225A3'

def lambda_handler(event, context):
    logger.info("Event: %s", event)
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

    # Ensure tags is a list of strings
    if not all(isinstance(tag, str) for tag in tags):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input parameters: Tags must be strings'}),
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
    # Retrieve all subscriptions once to improve efficiency
    try:
        subscriptions_response = sns.list_subscriptions_by_topic(TopicArn=TOPIC_ARN)
        subscriptions = subscriptions_response.get('Subscriptions', [])
        logger.info("Retrieved %d subscriptions", len(subscriptions))
    except Exception as e:
        logger.error("Error retrieving subscriptions: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error retrieving subscriptions', 'message': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }
        
    table = dynamodb.Table(TABLE_NAME)
    
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
        username = item['username']

        if operation_type == 1:
            updated_tags = current_tags + tags
            results.append({'url': url, 'status': 'Tags updated'})
        else:
            updated_tags = current_tags[:]
            nonexistent_tags = [tag for tag in tags if tag not in updated_tags]

            if nonexistent_tags:
                logger.warning("Tags to remove not found for URL: %s", url)
                results.append({'url': url, 'status': 'Tags to remove not found', 'nonexistent_tags': nonexistent_tags})
            else:
                for tag in tags:
                    updated_tags.remove(tag)
                results.append({'url': url, 'status': 'Tags removed'})

        table.update_item(
            Key={'username': item['username'], 'key': item['key']},
            UpdateExpression="SET tags = :tags",
            ExpressionAttributeValues={":tags": updated_tags}
        )
        
        for subscription in subscriptions:
            try:
                sub_attrs_response = sns.get_subscription_attributes(SubscriptionArn=subscription['SubscriptionArn'])
                sub_attrs = sub_attrs_response.get('Attributes', {})
                filter_policy = json.loads(sub_attrs.get('FilterPolicy', '{}'))
                logger.info("Subscription %s: Filter policy %s", subscription['SubscriptionArn'], filter_policy)

                if any(tag in filter_policy.get('tag', []) for tag in tags) and username in filter_policy.get('username', []):
                    message = f"{tags} is {'add' if operation_type == 1 else 'remove'}ed in {item['thumbnail_url']} by {username}"
                    logger.info("Publishing message to SNS: %s", message)
                    response = sns.publish(
                        TopicArn=TOPIC_ARN,
                        Message=json.dumps(message),
                        Subject="Tag Update Notification",
                        MessageAttributes={
                            'tag': {'DataType': 'String.Array', 'StringValue': json.dumps(tags)},
                            'username': {'DataType': 'String', 'StringValue': username}
                        }
                    )
                    logger.info("Published SNS message: %s", response)
            except Exception as e:
                logger.error("Error processing subscription %s: %s", subscription['SubscriptionArn'], str(e))

    return {
        'statusCode': 200,
        'body': json.dumps({'results': results}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        }
    }
