FROM golang:1.22-alpine
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["sh","-lc","go run -trimpath main.go"]
