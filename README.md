# Chat AIS

> Using ChatGPT to answer questions about maritime activity using AIS data.

## Setup up docker environment

Pre-requisites:

- Docker for Desktop 🐳
- Git 

First, you will need to clone this repository to your computer:

```sh
git clone https://github.com/Channel-Logistics/MHW-2022.git
```

Open the folder in your favorite IDE, then switch to the chat-ais branch:

```sh
git checkout chat-ais
```

Assuming you have docker properly configured for your system (checkout the docker instructions on main branch if unsure), build the docker image with the following command:

```sh
docker build -t chat_ais .
```

After the build has completed, start a container with the following command:

```sh
docker run -it -–name chat_ais -v <source_dir>:/src --entrypoint bash chat_ais
```

Make sure you use the absolute path of your local src folder as the source_dir parameter.

