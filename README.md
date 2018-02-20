It is necessary to set globally:
1) Docker CE https://docs.docker.com/install/
2) Docker Compose https://docs.docker.com/compose/install/

You need to go to the directory with the Dockerfile of the cloned repository, then:
1) Create Image: "docker build -t tornado_alpine ."
2) Run Container: "docker-compose up"

The default URL for working with the application localhost:8888/manage/

To create an image, you need a link to the github repository with a Dockerfile, like this: https://github.com/Sergeivb/async_test
