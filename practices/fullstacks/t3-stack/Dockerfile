# syntax=docker/dockerfile:1
# check=error=true

ARG NODE_VERSION=22

FROM node:${NODE_VERSION}-slim AS base
WORKDIR /app
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci

FROM base AS development
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM base AS build
ENV NODE_ENV=production
COPY . .
RUN npm run build
