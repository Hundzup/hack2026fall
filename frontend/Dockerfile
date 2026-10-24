FROM node:26 AS build-static

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm build

FROM docker.angie.software/angie:template

COPY --from=build-static /app/build/ /var/www/html
