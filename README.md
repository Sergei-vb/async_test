# Async_test

## Table of contents
- [Getting Started](#getting-started)
  * [Dependencies](#dependencies)
  * [Installation](#installation)
- [Documentation](#documentation)
  * [Run project](#run-project)
  * [Run in virtualenv](#run-in-virtualenv)
  * [Create Image](#create-image)

## Getting started

### Dependencies
#### This application works in conjunction with:
* https://github.com/HighHopesInt/HighHopes
* https://github.com/Sergei-vb/docker_database

### Installation
1. [Docker](https://docs.docker.com/install/ "Docker")
2. [Docker compose](https://docs.docker.com/compose/install/ "Docker compose")

## Documentation
### Run project
You need to go to the directory with the Dockerfile of the cloned repository, then:
1. Create Image: ```docker build -t NAME_YOUR_IMAGE .```
2. Enter the parameters of the docker-compose.yml:
   * ```image: ```NAME_YOUR_IMAGE
3. Run Container: ```docker-compose up```

### Run in virtualenv
in terminal:
* patching:
   * ```cp file.patch /CATALOG_VIRTUALENV/lib/python3.6/site-packages/tornado```
   * ```cd /CATALOG_VIRTUALENV/lib/python3.6/site-packages/tornado```
   * ```patch -p0 < file.patch```
* ```PORT=8888 ./hello_world.py```
* ```celery worker -A messaging.tasks -E -D -l=DEBUG &```
* ```celery flower```

#### Stop the celery worker
* ```pkill -9 -f 'celery worker' &```

### Create image
To create an image, you need a link to the github repository with a Dockerfile, like this: ```https://github.com/Sergeivb/async_test```