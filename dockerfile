FROM amazonlinux:2.0.20210219.0 as build-image

ARG FUNCTION_DIR="/src"
RUN yum install -y wget gzip gcc make

COPY ./.bashrc /root/.bashrc

RUN wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh \
	&& chmod 777 Anaconda3-2022.05-Linux-x86_64.sh \
	&& ./Anaconda3-2022.05-Linux-x86_64.sh -b -f \
	&& export PATH="/root/anaconda3/bin:$PATH"

# Clean up
RUN yum update -y \
    && yum remove -y wget \
    && yum autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# copy environement file into /src folder
RUN mkdir -p ${FUNCTION_DIR}
COPY ./environment.yml ${FUNCTION_DIR}

RUN /root/anaconda3/bin/conda update -y -n base -c defaults conda \
	&& /root/anaconda3/bin/conda env update -n chat_ais --file /src/environment.yml

# copy rest of files into /src
COPY ./ ${FUNCTION_DIR}

ENV LD_LIBRARY_PATH=/usr/local/lib

WORKDIR ${FUNCTION_DIR}
ENTRYPOINT /root/anaconda3/bin/conda run -n chat_ais python3 main.py