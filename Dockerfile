FROM alpine:3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

RUN apk add --no-cache python3 fortune && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install -r requirements.txt && \
    cp file.patch /usr/lib/python3.6/site-packages/tornado && \
    cd /usr/lib/python3.6/site-packages/tornado && \
    patch -p0 < file.patch
