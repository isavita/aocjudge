# syntax=docker/dockerfile:1
FROM ubuntu:24.04

ARG LDC_VERSION=1.41.0
ARG TARBALL=ldc2-${LDC_VERSION}-linux-aarch64.tar.xz
ARG URL=https://github.com/ldc-developers/ldc/releases/download/v${LDC_VERSION}/${TARBALL}

# syntax=docker/dockerfile:1
FROM ubuntu:24.04

ARG LDC_VERSION=1.41.0
ARG TARBALL=ldc2-${LDC_VERSION}-linux-aarch64.tar.xz
ARG URL=https://github.com/ldc-developers/ldc/releases/download/v${LDC_VERSION}/${TARBALL}

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl xz-utils libatomic1 build-essential \
  && curl -L "$URL" -o /tmp/$TARBALL \
  && tar -C /opt -xJf /tmp/$TARBALL \
  && ln -s /opt/ldc2-${LDC_VERSION}-linux-aarch64/bin/ldc2  /usr/local/bin/ldc2 \
  && ln -s /opt/ldc2-${LDC_VERSION}-linux-aarch64/bin/ldmd2 /usr/local/bin/ldmd2 \
  && useradd -m -s /bin/sh runner \
  && rm -rf /var/lib/apt/lists/* /tmp/$TARBALL

WORKDIR /app
USER runner
ENTRYPOINT ["ldc2","-run","/app/main.d"]
