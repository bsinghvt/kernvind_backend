#!/usr/bin/env bash

SERVICE_NAME=kernvind
IMAGE=kernvind/api_services
REPO=539247470170.dkr.ecr.us-east-2.amazonaws.com
docker build --build-arg SERVICE_NAME=$SERVICE_NAME -f $SERVICE_NAME/Dockerfile -t $IMAGE .
docker tag $IMAGE:latest $REPO/$IMAGE:latest
docker push $REPO/$IMAGE:latest