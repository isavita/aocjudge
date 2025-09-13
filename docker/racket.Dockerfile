FROM racket/racket:latest
RUN useradd -r -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["racket","/app/main.rkt"]
