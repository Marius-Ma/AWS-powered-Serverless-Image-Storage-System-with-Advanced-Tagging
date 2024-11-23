import json
import boto3

# Initialize AWS clients
sns = boto3.client('sns')

# Configuration
TOPIC = "arn:aws:sns:us-east-1:966781677907:fit5225a3"

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        email = data['email']
        tag = data['tag']
        username = data['username']

        # Find existing subscription
        subscription_arn = find_subscription(email, sns)
        result = ""
        
        if subscription_arn:
            # Get existing subscription attributes
            response = sns.get_subscription_attributes(
                SubscriptionArn=subscription_arn
            )
            filter_policy = json.loads(response['Attributes'].get('FilterPolicy', '{}'))

            # Update filter policy to include tag and username if not already included
            updated = False
            if 'tag' not in filter_policy:
                filter_policy['tag'] = [tag]
                updated = True
            elif tag not in filter_policy['tag']:
                filter_policy['tag'].append(tag)
                updated = True

            if 'username' not in filter_policy:
                filter_policy['username'] = [username]
                updated = True
            elif username not in filter_policy['username']:
                filter_policy['username'].append(username)
                updated = True

            if updated:
                # Update the subscription attributes with the new filter policy
                sns.set_subscription_attributes(
                    SubscriptionArn=subscription_arn,
                    AttributeName='FilterPolicy',
                    AttributeValue=json.dumps(filter_policy)
                )
                result = f'Subscription updated for {email} with tag {tag} and username {username}'
        else:
            # Create a new subscription with tag and username in the filter policy
            sns.subscribe(
                TopicArn=TOPIC,
                Protocol='email',
                Endpoint=email,
                Attributes={
                    'FilterPolicy': json.dumps({
                        'tag': [tag],
                        'username': [username]
                    })
                }
            )
            result = f'Subscription created for {email} with tag {tag} and username {username}'
        
        # Return the result
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing subscription: {str(e)}'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }

def find_subscription(endpoint, sns):
    """Find the subscription ARN for a given email endpoint."""
    response = sns.list_subscriptions_by_topic(TopicArn=TOPIC)
    for subscription in response['Subscriptions']:
        if subscription['Endpoint'] == endpoint:
            return subscription['SubscriptionArn']
    return None
