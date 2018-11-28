## to build:
#
# docker build -t halprin/fcli .
#
## to run:
#
# docker run -v ~/.fcli:/.fcli halprin/fcli fcli [...]
#
# -v adds a mapping so that your ~/.fcli is accessible in the container
# halprin/fcli is the image to run
# fcli is the command to run
# [...] are the arguments to the fcli commandFROM alpine:latest

# use Alpine Linux -- the resulting image is ~88mb
#FROM alpine:latest # 88mb
#FROM jfloff/alpine-python:3.4-slim # 94mb
FROM python:3-alpine 
# 169mb

# set the HOME environment variable
ENV HOME /

# set the working directory
WORKDIR /

# enable the community repository
RUN grep -qE '^[^#]*http://dl-cdn.alpinelinux.org/alpine/latest-stable/community$' /etc/apk/repositories || echo 'http://dl-cdn.alpinelinux.org/alpine/latest-stable/community' >> /etc/apk/repositories

# pull down the latest package lists
run apk update

# install basic packages we'll need later
RUN apk add \
curl \
git \
gcc \
linux-headers \
musl-dev \
python3-dev \
&& curl "https://bootstrap.pypa.io/get-pip.py" > /usr/bin/get-pip.py \
&& python3 /usr/bin/get-pip.py \
&& pip install pip --upgrade \
&& pip install -Iv \
  astroid==2.0.4 \
  autopep8==1.4.2 \
  certifi==2018.10.15 \
  chardet==3.0.4 \
  Click==7.0 \
  click-datetime==0.2 \
  idna==2.7 \
  isort==4.3.4 \
  lazy-object-proxy==1.3.1 \
  mccabe==0.6.1 \
  pep8==1.7.1 \
  pycodestyle==2.4.0 \
  pylint==2.1.1 \
  requests==2.20.0 \
  six==1.11.0 \
  typed-ast==1.1.0 \
  urllib3==1.24 \
  wrapt==1.10.11 \
  fcli \
&& apk del \
  musl-dev \
  linux-headers \
  gcc \
  git \
  curl
