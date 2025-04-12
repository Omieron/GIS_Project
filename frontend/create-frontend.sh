#!/bin/bash

docker build -t frontend-app .
docker stop frontend-container 2>/dev/null && docker rm frontend-container 2>/dev/null
docker run -d -p 8080:80 --name frontend-container frontend-app