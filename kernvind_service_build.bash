#!/usr/bin/env bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 539247470170.dkr.ecr.us-east-1.amazonaws.com
SERVICE_NAME=kernvind
IMAGE=kernvind/api_services
#DOCKER_REO=baljotsingh/kernvind-api-service
#DOCKER_IMAGE_TAG=api
REPO=539247470170.dkr.ecr.us-east-1.amazonaws.com
docker build --build-arg SERVICE_NAME=$SERVICE_NAME -f $SERVICE_NAME/Dockerfile -t $IMAGE .
docker tag $IMAGE:latest $REPO/$IMAGE:latest
docker push $REPO/$IMAGE:latest
#docker tag $IMAGE:latest $DOCKER_REO:$DOCKER_IMAGE_TAG
#docker push $DOCKER_REO:$DOCKER_IMAGE_TAG