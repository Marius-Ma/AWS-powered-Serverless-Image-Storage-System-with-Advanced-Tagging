# AWS Lambda Functions and API Gateway Setup Guide

This guide will help you set up four AWS Lambda functions and expose them through API Gateway. The functions included are `DeleteImageFunction.py`, `GetImageFromThumbnail.py`, `ManageTags.py`, and `SearchImageByTags.py`.

## Step 1: Create the Lambda Functions

1. **Go to the AWS Management Console.**
2. **Navigate to Lambda > Functions.**
3. **Click Create function.**
4. **Choose Author from scratch.**
5. **Enter the function name:**
   - `DeleteImageFunction`
   - `GetImageFromThumbnail`
   - `ManageTags`
   - `SearchImageByTags`
   - `GetImageByTagsOfImage`
6. **Choose the runtime as Python 3.8. For `GetImageByTagsOfImage`, choose Python 3.12.**
7. **Under Permissions, choose Use an existing role and select the labRole.**
8. **Click Create function.**
9. **Upload the corresponding Python script for each function:**
   - For `DeleteImageFunction.py`, `GetImageFromThumbnail.py`, `ManageTags.py`, `GetImageByTagsOfImage.py`, `SearchImageByTags.py`.
10. **For "GetImageByTagsOfImage" only, also upload the object_detection.py script and add the OpenCV and YOLO layers.**

## Step 2: Create and Configure API Gateway

1. **Create a new API:**
   - Go to the AWS Management Console.
   - Navigate to **API Gateway**.
   - Click **Create API**.
   - Choose **HTTP API**.
   - Click **Build**.

2. **Configure routes and integrate with Lambda:**
   - **Add routes:**
     - Click **Routes** > **Create**.
     - Add the following routes:
       - `/deleteImage` - POST
       - `/getImageByThumbnail` - GET
       - `/manageTags` - POST
       - `/searchByTags` - POST
       - `/getImagesByImage` - POST

   - **Integrate with Lambda:**
     - For each route, click on the route and then click **Attach integration**.
     - Choose **Lambda**.
     - Select the corresponding Lambda function (e.g., `DeleteImageFunction`, `GetImageFromThumbnail`, `ManageTags`, `SearchImageByTags`, `GetImageByTagsOfImage`).

3. **Deploy the API:**
   - Click **Deployments**.
   - Click **Create**.
   - Enter a stage name (e.g., `prod`).
   - Click **Deploy**.

## Step 3: Test the API

Use tools like Postman or a web browser to test the endpoints.

- **Delete Image Function:**
  - Sample Endpoint: `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/deleteImage`
  - Method: POST
  - Sample Request Body:
    ```json
    {
      "urls": [
        "https://fit5225-test-yuki.s3.amazonaws.com/thumbnails/yuki/8cf32708f2f04763b2ea87e7a1692dab.jpg",
        "https://fit5225-test-yuki.s3.amazonaws.com/thumbnails/marious/554586e4950e4576aadd6403d6b7d383.jpg"
      ]
    }
    ```

- **Get Image from Thumbnail:**
  - Sample Endpoint: `https://oxb5dfof7f.execute-api.us-east-1.amazonaws.com/pixTag/GetImageByThumbnail?thumbnail_url=https://fit5225-test-yuki.s3.amazonaws.com/thumbnails/yuki/8cf32708f2f04763b2ea87e7a1692dab.jpg`
  - Method: GET

- **Manage Tags:**
  - Sample Endpoint: `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/manageTags`
  - Method: POST
  - Sample Request Body:
    ```json
    {
      "url": ["https://fit5225-test-yuki.s3.amazonaws.com/thumbnails/mike/6e440ae0b4d04340b8ddafbfe74e6826.jpg"],
      "type": 1,
      "tags": ["person", "outdoor"]
    }
    ```

- **Search Images by Tags:**
  - Sample Endpoint: `https://pyfhc6s7fi.execute-api.us-east-1.amazonaws.com/pixTag/searchByTags`
  - Method: POST
  - Sample Request Body:
    ```json
    {
      "username": "mike",
      "tags": [
          "alien,1",
          "dog,1"
        ]
    }
    ```

- **Search Images by Tags of an Image:**
  - Sample Endpoint: `https://pyfhc6s7fi.execute-api.us-east-1.amazonaws.com/pixTag/getImagesByImage`
  - Method: POST
  - Sample Request Body:
    ```json
    {
      "username": "mike",
      "file": "Your base64 encoded image data here"
    }
    ```