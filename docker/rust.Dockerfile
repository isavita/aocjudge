# syntax=docker/dockerfile:1
FROM rust:1.80-bookworm

# Ensure a system linker is available for rustc
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc libc6-dev ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -s /bin/sh runner

# Small wrapper: compile single-file /app/main.rs to /tmp/app (writable tmpfs), then exec it.
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -e' \
  'export HOME=/tmp' \
  'export RUST_BACKTRACE=0' \
  '/usr/local/cargo/bin/rustc -O -C codegen-units=1 -C debuginfo=0 -o /tmp/app /app/main.rs' \
  'exec /tmp/app' > /usr/local/bin/run-rust && chmod +x /usr/local/bin/run-rust

USER runner
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/run-rust"]
