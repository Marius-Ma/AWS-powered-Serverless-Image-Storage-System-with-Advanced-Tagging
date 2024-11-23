# Daily Record
## 19/05/2024
We had our first Zoom meeting, where we read through the assignment 3 requirements together and drafted the first version of the architecture diagram.
## 26/05/2024
We conducted our second Zoom meeting, updated the second version of the architecture diagram, and explored AWS API Gateway and User Pool together as a team. We also divided the tasks, and it is preliminarily planned that I will start writing the first three Lambda functions.
## 27/05/2024
Today, I will start working on the first Lambda function, 'ImageUploadHandler,' which will be used to upload images. 

After reviewing the project description again, I believe that thumbnails should also be stored in the S3 bucket. Therefore, I think we should merge the upload image and thumbnail generation into one Lambda function. When the user uploads an image, a thumbnail will also be generated and stored in the S3 bucket. I have already merged them.
## 28/05/2024
Today, I will test this Lambda function in AWS to see if any improvements are needed.

After debugging and testing, I have completed the first Lambda function and successfully uploaded a image with generated thumbnail to S3 using Postman. I will continue to explore the second Lambda function.
## 29/05/2024
Last night, we successfully deployed Lambda1 on the demo machine via Zoom with Hongyi Liu. Today, I will continue exploring Lambda2 for image detection.
## 30/05/2024
Yesterday, I successfully wrote the image detection Lambda function. Today, I will continue to refine the image detection Lambda, as well as test and debug it.
## 31/05/2024
Yesterday, I had a Zoom meeting with Yuki and Hongyi Liu, guiding them to deploy my two Lambda functions. Today, I plan to explore how to deploy AWS SNS for our assignment.
## 01/06/2024
The deployment was successful yesterday. Today, I plan to test if AWS SNS can successfully send an email when I upload an image.
## 02/06/2024
Today, I will continue testing AWS SNS and attempt to write a new Lambda function.
## 03/06/2024
Today, I will try to debug and improve the architecture diagram.
## 04/06/2024
Today, I will try to write the team report about architecture diagram.
## 05/06/2024
Today, I will upload the final version of the Architecture diagram and start writing my individual report.
