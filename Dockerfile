FROM bamx23/scipy-alpine:latest
MAINTAINER "NOMAD Team"
# Create all the necessary folders
RUN mkdir -p /var/cache/apk \
    && ln -s /var/cache/apk /etc/apk/cache

RUN mkdir -p /usr/local/python-server/


# Copy over the verison file
ADD python-server.version /

# Copy over all source files
WORKDIR /usr/local/python-server/
COPY . .
RUN chmod -R 775 /usr/local/python-server/

# Install all the requirements
RUN apk add --upgrade --no-cache py-setuptools
RUN yes | pip install --upgrade --no-cache-dir pip && yes | pip install --no-cache-dir -r requirements.txt

#RUN apt-get update \
#    && apt-get install -y python-pip python-dev build-essential \
#    && yes | pip install --upgrade pip \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*
# Set correct environment variables and working directory
ENV FLASK_APP=/usr/local/python-server/Spectrum.py
WORKDIR /
ENTRYPOINT ['/usr/local/python-server/startContainer.sh']