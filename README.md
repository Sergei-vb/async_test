# coralline-rpc

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
* https://github.com/HighHopesInt/coralline-dashboard
* https://github.com/Sergei-vb/coralline-components

### Installation
1. [Docker](https://docs.docker.com/install/ "Docker")
2. [Docker compose](https://docs.docker.com/compose/install/ "Docker compose")

## Documentation
### Run project
You need to go to the directory with the Dockerfile of the cloned repository, then:
1. Create Image: ```docker build -t NAME_YOUR_IMAGE .```
2. Enter image name and then parameters of connect to DB to the docker-compose.yml:
   * ```image: ```NAME_YOUR_IMAGE
   * ```NAME: ```
   * ```USER: ```
   * ```PASSWORD: ```
   * ```HOST: ```
   * ```PORTDB: ```
3. Run Container: ```docker-compose up```

### Run in virtualenv
* You need setup:
  * [Supervisor (use package manager)](http://supervisord.org/installing.html#installing-a-distribution-package "Supervisor")
  * [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/ "Virtualenv")
  * [Python 3.5](https://www.python.org/downloads/ "Python3.5")

* and run script:
  * Fill fill.sh of your data.
  * ```./scripts/start.sh```

### Create image
To create an image, you need a link to the github repository with a Dockerfile, like this: ```https://github.com/Sergeivb/coralline-rpc```