FROM amazonlinux:2.0.20210219.0 as build-image

# use following command to build image
# docker build -t <image_name> .

# build image arguments
ARG GDAL_VERSION=3.0.4
ARG SOURCE_DIR=/usr/local/src/python-gdal
ARG FUNCTION_DIR="/src"
ARG DEPENDENCY_DIR="/depend"

# install dependencies for proj and gdal
RUN yum install -y wget gzip gcc make
RUN yum install -y automake libtool pkg-config libsqlite3-dev sqlite3 

# install python 3.7, pip, and python development tools
RUN yum install -y python37 && \
    yum install -y python3-pip && \
    yum install -y python-devel python3-devel

# gonna be honest - prob don't need most of this but it installs some dependency that makes the build complete
RUN yum groupinstall -y "Development Tools" --setopt=group_package_types=mandatory,default,optional

# Get EPEL release to install sqlite-devel dependency
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install -y sqlite-devel.x86_64

# Build against PROJ master (which will be released as PROJ 6.0)
RUN wget "http://download.osgeo.org/proj/proj-6.0.0.tar.gz" \
&& tar -xzf proj-6.0.0.tar.gz \
&& mv proj-6.0.0 proj \
&& echo "#!/bin/sh" > proj/autogen.sh \
&& chmod +x proj/autogen.sh \
&& cd proj \
&& ./autogen.sh \
&& CXXFLAGS='-DPROJ_RENAME_SYMBOLS' CFLAGS='-DPROJ_RENAME_SYMBOLS' ./configure --disable-static --prefix=/usr/local \
&& make -j"$(nproc)" \
&& make -j"$(nproc)" install

# Get latest GDAL source, compile and install
RUN mkdir -p "${SOURCE_DIR}" \
    && cd "${SOURCE_DIR}" \
    && wget "http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz" \
    && tar -xvf "gdal-${GDAL_VERSION}.tar.gz" \
    && cd "gdal-${GDAL_VERSION}" \
    && ./configure --with-python --with-curl --with-openjpeg --without-libtool --with-proj=/usr/local \
    && make -j"$(nproc)" \
    && make install \
    && export LD_LIBRARY_PATH=/usr/local/lib \
    && ldconfig

# Install GDAL python wrapper
RUN python3.7 -m pip install GDAL==${GDAL_VERSION} \
    && cd /usr/local

# Install Python packages
RUN python3.7 -m pip install --upgrade pip && \
    python3.7 -m pip install pandas && \
    python3.7 -m pip install numpy && \
    python3.7 -m pip install geopandas && \
    python3.7 -m pip install s3fs && \
    python3.7 -m pip install fsspec && \
    python3.7 -m pip install boto3 && \
    python3.7 -m pip install psycopg2 && \
    python3.7 -m pip install tensorflow && \
    python3.7 -m pip install pyarrow

# Clean up
RUN yum update -y \
    && yum remove -y wget \
    && yum autoremove -y

# copy dependencies into /depend folder in the container
RUN mkdir -p ${DEPENDENCY_DIR}
COPY depend/* ${DEPENDENCY_DIR}

# copy source code into /src folder in the container
RUN mkdir -p ${FUNCTION_DIR}
COPY src/* ${FUNCTION_DIR}

# make ~/.aws directory and copy config and credential files into it
# this is required in order to use boto3 to access files from s3
RUN mkdir -p ~/.aws \
    && cp /depend/config ~/.aws/config \
    && cp /depend/credentials ~/.aws/credentials

FROM amazonlinux:2.0.20210219.0

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Can't run docker container the normal way since there is an issue with an environment variable
# not being set properly. Instead, we run this bash script that sets the environment variable
ENTRYPOINT [ "/bin/bash", "/depend/start.sh" ]