#!/bin/sh
# Build all runtime images and server image.
# Optionally provide a registry/user prefix (default: baruh).
set -e

REGISTRY="${1:-baruh}"

docker build -t "$REGISTRY/aocjudge-rs" -f docker/rust.Dockerfile .
docker build -t "$REGISTRY/aocjudge-py" -f docker/python.Dockerfile .
docker build -t "$REGISTRY/aocjudge-js" -f docker/javascript.Dockerfile .
docker build -t "$REGISTRY/aocjudge-rb" -f docker/ruby.Dockerfile .
docker build -t "$REGISTRY/aocjudge-d" -f docker/d.Dockerfile .
docker build -t "$REGISTRY/aocjudge-rkt" -f docker/racket.Dockerfile .
docker build -t "$REGISTRY/aocjudge-server" -f docker/server.Dockerfile .
