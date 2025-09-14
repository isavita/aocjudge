FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      racket \
      ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -r -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["racket","/app/main.rkt"]
