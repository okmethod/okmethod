# syntax=docker/dockerfile:1
# check=error=true

ARG GO_VERSION=1.23
ARG AIR_VERSION=1.61.1
ARG DEBIAN_VERSION=12

FROM golang:${GO_VERSION} AS base
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download && go mod verify

FROM base AS development
ARG AIR_VERSION
RUN go install github.com/air-verse/air@v${AIR_VERSION}
COPY . .

FROM base AS build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /app/main main.go

FROM gcr.io/distroless/static-debian${DEBIAN_VERSION}:latest AS production
WORKDIR /app
COPY --from=build /app/main ./main
CMD ["./main"]
