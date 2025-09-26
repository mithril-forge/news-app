# Multi-target Dockerfile for both development and production

# Base stage - common for both dev and prod
FROM node:20-alpine AS base

WORKDIR /app
COPY package.json package-lock.json* ./

RUN npm ci
COPY . .

# Set common environment variables
ENV NEXT_TELEMETRY_DISABLED=1

# === Development target ===
FROM base AS development

ENV ENVIRONMENT=development
ENV SKIP_ENV_VALIDATION=1
ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true

EXPOSE 3000
CMD ["npm", "run", "dev"]

# === Production target ===
FROM base AS production
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_CONTAINER_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_CONTAINER_API_URL=$NEXT_PUBLIC_CONTAINER_API_URL
ENV ENVIRONMENT=production

RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
