import json
import boto3
import ObjectDetection

# Initialize AWS service clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Configuration parameters
TOPIC = "arn:aws:sns:us-east-1:966781677907:fit5225a3"
DYNAMODB_TABLE = "fit5225A3"
IMAGE_FOLDER = "images/"
THUMBNAIL_FOLDER = "thumbnails/"

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            # Parse the S3 event
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            image = s3.get_object(Bucket=bucket, Key=key)
            image_body = image['Body'].read()

            # Identify tags within the image
            tags = ObjectDetection.readbytes(image_body)  # Assume it returns a list of tags

            # Extract the uploader's username (from the file path)
            username = key.split('/')[1]  # Assuming the path format "images/username/file.jpg"

            # Generate thumbnail URL
            thumbnail_key = key.replace(IMAGE_FOLDER, THUMBNAIL_FOLDER)
            image_url = f"https://{bucket}.s3.amazonaws.com/{key}"
            thumbnail_url = f"https://{bucket}.s3.amazonaws.com/{thumbnail_key}"

            # Save image information to DynamoDB
            table = dynamodb.Table(DYNAMODB_TABLE)
            table.put_item(Item={
                'username': username,
                'key': key,
                'tags': tags,
                'image_url': image_url,
                'thumbnail_url': thumbnail_url
            })

            # Retrieve all subscriptions for the topic
            subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC)
            for subscription in subscriptions['Subscriptions']:
                subscription_arn = subscription['SubscriptionArn']
                response = sns.get_subscription_attributes(SubscriptionArn=subscription_arn)
                filter_policy = json.loads(response['Attributes'].get('FilterPolicy', '{}'))

                # Check the subscription filter policy for each tag
                for tag in tags:
                    if 'tag' in filter_policy and tag in filter_policy['tag'] and 'username' in filter_policy and username in filter_policy['username']:
                        # Send an SNS notification
                        sns.publish(
                            TopicArn=TOPIC,
                            Message=f"New image uploaded by {username} with tag {tag}. See image at {image_url} and thumbnail at {thumbnail_url}",
                            Subject="New Image Notification",
                            MessageAttributes={
                                'tag': {'DataType': 'String', 'StringValue': tag},
                                'username': {'DataType': 'String', 'StringValue': username}
                            }
                        )

        return {'statusCode': 200, 'body': json.dumps('Successfully processed image and stored tags with URLs')}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(f'Error processing image: {str(e)}')}

