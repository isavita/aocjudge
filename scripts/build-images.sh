#!/bin/sh
set -e

docker build -t aocjudge-rs -f docker/rust.Dockerfile .
docker build -t aocjudge-py -f docker/python.Dockerfile .
docker build -t aocjudge-js -f docker/javascript.Dockerfile .
docker build -t aocjudge-rb -f docker/ruby.Dockerfile .
docker build -t aocjudge-d  -f docker/d.Dockerfile .
docker build -t aocjudge-rkt -f docker/racket.Dockerfile .
