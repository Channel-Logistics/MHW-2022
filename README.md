# Miami Hack Week 2022

> Hello! Welcome to Miami and thanks for joining the Space Eyes house. Here are some instructions on how to setup your development environment to start building your project. 

## Setup up docker environment

Pre-requisites:

- Docker for Desktop 🐳
- Git 

First, you will need to clone this repository to your computer:

```sh
git clone https://github.com/Channel-Logistics/MHW-2022.git
```

Open the folder in your favorite IDE, then please create a branch with your own name to develop on:

```sh
git branch <name>
git checkout <name>
```

Next, open up the credentials file under the /depend directory. Input your AWS access key and secret access key that was provided to you during orientation. If you do not have these, please ask a Space Eyes employee for help. 

Assuming you have docker properly configured for your system (checkout the docker instructions if unsure), build the docker image with the following command:

```sh
docker build -t <image_name> .
```

The build process will take 5-7 minutes to complete. After the build has completed, start a container with the following command:

```sh
docker run -it –name <container_name> -v <source_dir>:<target_dir> <image_name>
```

Make sure you use the absolute path of your local src folder as the source_dir parameter and then the "/src" directory as the target_dir parameter.

Quick note - sometimes gdal will throw the following error if you try to import it from python:
> ImportError: libgdal.so: cannot open shared object file: No such file or directory

If you see this, the LD_LIBRARY_PATH environment variable is not set. Run the following command to correct it:

```sh
export LD_LIBRARY_PATH=/usr/local/lib
```

This is automatically done on startup, so you shouldn't have to worry about it. 

This should complete your development environment! If you have any questions, ask a Space Eyes employee or feel free to DM Alex on Discord.

## Reading data from S3

Reading data from S3 is really easy if you're using the provided docker environment:

```sh
df = pd.read_parquet(<s3_uri>)
```

If this did not work, you are either missing the ffspec and/or s3fs python dependencies or you are missing valid credentials under the ~/.aws directory. 