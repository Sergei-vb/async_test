FROM alpine:3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# RUN echo deb http://ru.archive.ubuntu.com/ubuntu/ xenial main universe > /etc/apt/sources.list

# RUN apt-get update && apt-get install -y python3-pip && apt-get clean && rm -rf /var/lib/apt/lists/* && pip3 install -r requirements.txt

RUN apk add --no-cache python3 fortune && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install -r requirements.txt

# Make the port available to the world outside this container
# EXPOSE 4000

# Define environment variable
# ENV NAME World

CMD ["./hello_world.py", "--logging=info", "--log-file-prefix=/var/log/hello_world.log"]

