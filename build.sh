#!/bin/bash

set -e

docker build -t isp-up:v1.1 .
docker run --env-file ./ISPup.env.vars --name ISPup -p 80:80 isp-up:v1.1
