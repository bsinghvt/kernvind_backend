#!/usr/bin/env bash

docker build --build-arg SERVICE_NAME=llm_chat_service -f llm_chat_service/Dockerfile  -t kernvind/chat_service .
docker tag kernvind/chat_service:latest 539247470170.dkr.ecr.us-east-2.amazonaws.com/kernvind/chat_service:latest
docker push 539247470170.dkr.ecr.us-east-2.amazonaws.com/kernvind/chat_service:latest