FROM dlanguage/dmd:latest-alpine
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["dmd", "-run", "/app/main.d"]
