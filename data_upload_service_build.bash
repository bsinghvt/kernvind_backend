#!/usr/bin/env bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 539247470170.dkr.ecr.us-east-1.amazonaws.com
SERVICE_NAME=data_upload_service
IMAGE=kernvind/data_upload_service
REPO=539247470170.dkr.ecr.us-east-1.amazonaws.com
docker build --build-arg SERVICE_NAME=$SERVICE_NAME -f $SERVICE_NAME/Dockerfile -t $IMAGE .
docker tag $IMAGE:latest $REPO/$IMAGE:latest
docker push $REPO/$IMAGE:latest