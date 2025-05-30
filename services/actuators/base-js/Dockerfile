FROM node:20-slim AS base
RUN apt-get update && \
    apt-get install --no-install-recommends -y wait-for-it
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN npm install -g pnpm@10.4
COPY package.json pnpm-lock.yaml /app/
WORKDIR /app

FROM base AS dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

FROM dependencies AS development
ENV NODE_ENV=development
COPY . /app
CMD ["pnpm", "dev"]

FROM dependencies AS build
COPY . /app
RUN pnpm build && pnpm prune --prod

FROM base AS production
ENV NODE_ENV=production
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/dist /app
CMD ["node", "index.js"]
