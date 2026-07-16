# Этап 1: сборка Vite
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# API доступен через nginx-прокси на том же домене
ENV VITE_API_BASE_URL=/api
RUN npm run build

# Этап 2: раздача статики через nginx
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
