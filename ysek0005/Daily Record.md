# Daily Record
## 19/05/2024
We had our first Zoom meeting, where we read through the assignment 3 requirements together and drafted the first version of the architecture diagram.
## 26/05/2024
We conducted our second Zoom meeting, updated the second version of the architecture diagram, and explored AWS API Gateway and User Pool together as a team. We also divided the tasks, and it is preliminarily planned that Mike will start writing the first three Lambda functions.
## 27/05/2024
Today, I will start working on the fourth Lambda function, 'QueryHandler' which will be used for Tag-based Image Search.

I have uploaded fourth and fifth lambdas and tested them with my own RDB and API gateway. 
I have also uploaded pymysql-layer.zip which will be used for layer in lambdas.
## 28/05/2024
Today, I will start working on the seventh lambda function, 'ManualTagManager' which will be used for  Manual Tag Management.

I have uploaded seventh lambda and tested it with postman.
I have also created lambda readme file for guideline. 
## 29/05/2024
Today, I will start working on the eighth lambda function, 'ImageDeleter' which will delete images from both s3 and RDB.

After checking, I found that we will use Dynamo DB, so I will revise the codes accordingly. I will continue to do this tomorrow.
## 30/05/2024
Today, I will continue to revise the codes and start working on the other lambdas.

I had a Zoom meeting with Mike, and he helped me to configure his lambdas into my AWS account.
After testing and debugging, I have integrated Mike's lambdas into my AWS account and tested my lambdas successfully.
I will continue to work on the last lambda which enable user to find images based on the tags of an image tomorrow. 
## 31/05/2024
Today I have created GetImageByTagsOfImage which finds images based on the tags of an image.

I will work on debugging my lambdas such as handling validation properly and improving efficiency for query.
## 2/6/2024
I have updated manageTags Lambda to allow duplicated tags.
## 3/6/2024
Today I will continue to improve my query lambdas.