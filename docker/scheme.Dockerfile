FROM alpine:latest
RUN apk add guile
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["guile","/app/main.scm"]
