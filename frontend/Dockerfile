# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Set the backend URL for Next.js rewrites at build time.
# Inside Docker, the backend is always reachable at http://backend:8000
ENV BACKEND_INTERNAL_URL=http://backend:8000

# Build Next.js
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public
COPY --from=builder /app/package*.json ./

RUN npm ci --only=production

# Create non-root user
RUN addgroup -g 10001 -S appuser && \
    adduser -u 10001 -S appuser -G appuser
USER appuser

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]