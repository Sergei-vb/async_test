# Async_test

## Table of contents
- [Getting Started](#getting-started)
  * [Dependencies](#dependencies)
  * [Installation](#installation)
- [Documentation](#documentation)
  * [Run project](#run-project)
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
1. Create Image: ```docker build -t tornado_alpine .```
2. Run Container: ```docker-compose up```

### Create image
To create an image, you need a link to the github repository with a Dockerfile, like this: ```https://github.com/Sergeivb/async_test```
