FROM ruby:3.2-alpine
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["ruby","/app/main.rb"]
