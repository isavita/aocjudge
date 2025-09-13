FROM python:3.11-alpine
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["python","/app/main.py"]
