Copy the code from ImageUploadHandler.py file into the AWS lambda function. Don't forget to change the s3 bucket name to your own s3 bucket name.

Please open the Dockerfile with VSCode, and then open the terminal to run the following command:

1. Build the Docker image:

docker build -t my-python3.12-image .

2. Run the Docker container to copy the packages to your current directory on the host:

docker run --rm -it -v $(pwd):/data my-python3.12-image cp -r /packages/opencv-python-3.12/python/ /data/python/

3. Zip the copied directory on your host machine:

zip -r opencv-python-312.zip python/


4. Open your AWS, please upload the zip file to the S3 bucket.

5. In the Lambda page, open the Layers section. Create a new layer using the zip file from S3. Finally, add the layer to your function in the Function page.
