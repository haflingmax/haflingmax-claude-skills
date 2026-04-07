# Storybook in Docker

When adding Storybook to a project that uses Docker, detect `docker-compose.yml` or
`Dockerfile` during project detection and automatically include Storybook in the
container infrastructure.

## Detection

If `docker-compose.yml` or `Dockerfile` exists in the project root, Storybook must be
containerized — not just installed as a dev dependency. Users expect to `docker compose up`
and have everything work, including Storybook.

## Dockerfile.storybook (Multi-stage: Build + Nginx)

Never run `storybook dev` in a container. Build as static site and serve via nginx:

```dockerfile
# Stage 1: Build
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Storybook + Vite builds consume significant memory
RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build-storybook

# Stage 2: Serve
FROM nginx:1.27-alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/storybook-static /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

> **Note:** If dependencies require postinstall hooks (e.g. Prisma), use `npm ci` without
> `--ignore-scripts`. Add `--ignore-scripts` only when you're sure no postinstall is needed.

## docker-compose.yml Service

```yaml
  storybook:
    build:
      context: ./frontend
      dockerfile: Dockerfile.storybook
    ports:
      - "${STORYBOOK_PORT:-6006}:80"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## .dockerignore (Critical for Performance)

Ensure the frontend `.dockerignore` excludes:
```
node_modules
.next
storybook-static
.git
coverage
playwright-report
```

## Verification Rule

After adding Storybook to a Docker project, verify the container builds and runs:
```bash
docker compose build storybook
docker compose up -d storybook
# Wait for container health check (retry up to 30s)
for i in $(seq 1 6); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6006 2>/dev/null)
  [ "$STATUS" = "200" ] && echo "Storybook is healthy" && break
  sleep 5
done
# STATUS must be 200
```

Only report the task as complete AFTER the container health check passes.

## Key Gotchas
- `NODE_OPTIONS="--max-old-space-size=4096"` is required — Storybook+Vite OOMs at default 512MB
- Final nginx image is ~30MB (vs ~1.5GB for node image with dev server)
- Use `npm run build-storybook -- --test` in CI to skip manager UI and speed up builds
- Port 6006 externally maps to port 80 inside the container
