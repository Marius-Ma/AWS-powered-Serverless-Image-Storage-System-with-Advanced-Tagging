import json
import base64
import boto3
import os
import uuid
import cv2
import numpy as np

s3 = boto3.client('s3')
BUCKET = "fit5225a3"  # S3 bucket name
MAX_DIMENSION = 100
IMAGE_FOLDER = "images/"
IMAGE_THUMBNAIL = "thumbnails/"

#image info: {"file": "imagebase64", "username": "", "name": "123.jpg"}

def lambda_handler(event, context):
    try:
        # Load the data from the event
        data = json.loads(event['body'])
        username = data['username']
        name = data['name']
        image = data['file']  # Ensure the 'file' key is used for the base64 image string
        
        _, suffix = os.path.splitext(name)
        img_id = uuid.uuid4()

        # Original image key
        key = IMAGE_FOLDER + username + "/" + str(img_id.hex) + suffix

        # Decode the base64 image
        img_decode = base64.b64decode(image)
        img_nparray = np.frombuffer(img_decode, np.uint8)  # Correct method to convert byte string to numpy array
        img_mat = cv2.imdecode(img_nparray, cv2.IMREAD_COLOR)

        # Generate thumbnail while maintaining aspect ratio
        height, width = img_mat.shape[:2]

        if width > height:
            new_width = MAX_DIMENSION
            new_height = int(height * (MAX_DIMENSION / width))
        else:
            new_height = MAX_DIMENSION
            new_width = int(width * (MAX_DIMENSION / height))

        img_thumbnail = cv2.resize(img_mat, (new_width, new_height), interpolation=cv2.INTER_AREA)
        _, img_thumbnail_bytes = cv2.imencode(suffix, img_thumbnail)
        img_thumbnail_bytes = img_thumbnail_bytes.tobytes()
        img_thumbnail_key = IMAGE_THUMBNAIL + username + "/" + str(img_id.hex) + suffix

        # Upload original image
        s3.put_object(Bucket=BUCKET, Key=key, Body=img_decode, ContentType='image/jpeg', ContentDisposition='inline')
        
        # Upload thumbnail image
        s3.put_object(Bucket=BUCKET, Key=img_thumbnail_key, Body=img_thumbnail_bytes, ContentType='image/jpeg', ContentDisposition='inline')

        return {
            'statusCode': 200,
            'body': json.dumps("Successfully uploaded image and generated thumbnail"),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps("Error uploading image and generating thumbnail"),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*'
            }
        }
