# syntax=docker/dockerfile:1
# check=error=true

ARG NODE_VERSION=22
ARG VITE_FASTAPI_PROXY_TARGET

FROM node:${NODE_VERSION}-slim AS base
WORKDIR /app
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci
ARG VITE_FASTAPI_PROXY_TARGET
ENV VITE_FASTAPI_PROXY_TARGET=${VITE_FASTAPI_PROXY_TARGET}

FROM base AS development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM base AS build
ENV NODE_ENV=production
COPY . .
RUN npm run build
