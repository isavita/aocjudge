FROM node:18-alpine
RUN npm install -g lodash
RUN adduser -D -s /bin/sh runner
USER runner
WORKDIR /app
ENTRYPOINT ["node","/app/main.js"]
