# Frontend Next.js de ShareU. Contexto de build: app/frontend.
#
# Equivale a `Dockploy/Dockerfile.web`; existe en la carpeta del frontend para
# que `docker compose up` de la raíz no dependa de la carpeta de despliegue.
FROM node:22-alpine AS construccion
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
# NEXT_PUBLIC_* se fija en el build: llega como build arg.
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=construccion /app/package.json ./
COPY --from=construccion /app/node_modules ./node_modules
COPY --from=construccion /app/.next ./.next
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:3000/ || exit 1
CMD ["node_modules/.bin/next", "start", "-H", "0.0.0.0", "-p", "3000"]
