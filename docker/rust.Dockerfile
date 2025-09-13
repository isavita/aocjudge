# syntax=docker/dockerfile:1
FROM rust:1.80-bookworm

# Ensure a system linker is available for rustc
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc libc6-dev ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -s /bin/sh runner

USER runner
WORKDIR /app
