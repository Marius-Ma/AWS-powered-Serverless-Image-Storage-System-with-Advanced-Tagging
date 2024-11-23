import json
import boto3
import ObjectDetection
import os

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Configuration
TOPIC = "arn:aws:sns:us-east-1:966781677907:fit5225a3"
DYNAMODB_TABLE = "fit5225A3"
IMAGE_FOLDER = "images/"
THUMBNAIL_FOLDER = "thumbnails/"

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Retrieve the uploaded image from S3
            image = s3.get_object(Bucket=bucket, Key=key)
            image_body = image["Body"].read()
            
            # Perform object detection to get tags
            tags = ObjectDetection.readbytes(image_body)
            
            # Get DynamoDB table
            table = dynamodb.Table(DYNAMODB_TABLE)
            
            # Extract username from the S3 key (assuming the format is images/username/file.jpg)
            parts = key.split("/")
            username = parts[1]
            
            # Generate the thumbnail S3 key
            thumbnail_key = key.replace(IMAGE_FOLDER, THUMBNAIL_FOLDER)
            
            # Construct S3 URLs
            image_url = f"https://{bucket}.s3.amazonaws.com/{key}"
            thumbnail_url = f"https://{bucket}.s3.amazonaws.com/{thumbnail_key}"
            
            # Create the item to store in DynamoDB
            item = {
                "username": username,
                "key": key,
                "tags": tags,
                "image_url": image_url,
                "thumbnail_url": thumbnail_url
            }
            
            # Print and save the item to DynamoDB
            print(item)
            table.put_item(Item=item)
            
            # Get subscriptions for the topic
            subscriptions = sns.list_subscriptions_by_topic(TopicArn=TOPIC)
            
            # Track if we have sent a message for this username and subscription
            sent_subscriptions = set()
            
            for subscription in subscriptions['Subscriptions']:
                subscription_arn = subscription['SubscriptionArn']
                
                # Get subscription attributes
                response = sns.get_subscription_attributes(
                    SubscriptionArn=subscription_arn
                )
                filter_policy = json.loads(response['Attributes'].get('FilterPolicy', '{}'))
                
                # Check if the username is in the filter policy
                if 'username' in filter_policy and username in filter_policy['username']:
                    message = f"User '{username}' uploaded an image with the tags: {', '.join(tags)}.\n\n"
                    sns.publish(
                        TopicArn=TOPIC,
                        Message=message,
                        Subject="New Image Uploaded",
                        MessageAttributes={
                            'tag': {
                                'DataType': 'String',
                                'StringValue': ', '.join(tags)
                            },
                            'username': {
                                'DataType': 'String',
                                'StringValue': username
                            }
                        })
                    
                    # Mark this subscription as sent
                    sent_subscriptions.add(subscription_arn)

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed image and stored tags with URLs')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing image')
        }
