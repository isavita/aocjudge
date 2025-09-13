FROM dlang2/dmd:2.106.0-alpine
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["dmd", "-run", "/app/main.d"]
