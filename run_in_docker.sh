#!/usr/bin/env bash

set -e

docker build .
docker run --rm -it -v `pwd`:/workspace -w /workspace `docker build -q .` bash ./fetch.sh
