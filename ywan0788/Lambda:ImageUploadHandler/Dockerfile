# Use the latest Amazon Linux as the base image
FROM amazonlinux:latest

# Set the working directory to the root
WORKDIR /

# Update the package manager and install necessary tools and libraries
RUN yum update -y \
    && yum install -y gcc openssl-devel wget tar gzip zlib zlib-devel

# Download Python 3.12 source code
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz

# Extract the downloaded tarball
RUN tar -xzvf Python-3.12.0.tgz

# Set the working directory to the extracted Python source
WORKDIR /Python-3.12.0

# Configure and install Python 3.12
RUN ./configure --enable-optimizations \
    && make install

# Create a directory for Python packages
RUN mkdir /packages

# Add the required package to the requirements file
RUN echo "opencv-python-headless" > /packages/requirements.txt

# Create the directory structure for the packages
RUN mkdir -p /packages/opencv-python-3.12/python/lib/python3.12/site-packages

# Install the required Python package into the specified directory
RUN pip3.12 install -r /packages/requirements.txt -t /packages/opencv-python-3.12/python/lib/python3.12/site-packages
