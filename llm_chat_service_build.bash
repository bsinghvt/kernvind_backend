#!/usr/bin/env bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 539247470170.dkr.ecr.us-east-1.amazonaws.com
docker build --build-arg SERVICE_NAME=llm_chat_service -f llm_chat_service/Dockerfile  -t kernvind/chat_service .
docker tag kernvind/chat_service:latest 539247470170.dkr.ecr.us-east-1.amazonaws.com/kernvind/chat_service:latest
docker push 539247470170.dkr.ecr.us-east-1.amazonaws.com/kernvind/chat_service:latest