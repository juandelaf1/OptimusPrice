FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system user && adduser --system user
COPY --from=builder --chown=user:user /app/.next ./.next
COPY --from=builder --chown=user:user /app/node_modules ./node_modules
COPY --from=builder --chown=user:user /app/package.json ./package.json
COPY --from=builder --chown=user:user /app/public ./public
COPY --from=builder --chown=user:user /app/src ./src

USER user
EXPOSE 3000
ENV PORT 3000
CMD ["npm", "run", "start"]