# Frontend Dockerfile (build React and serve with Nginx)
FROM node:18-alpine AS build
WORKDIR /app
# With build context set to ./frontend, copy files directly
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . ./
RUN npm run build

FROM nginx:alpine AS prod
# Copy built frontend
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx config (proxies /api to backend service)
COPY nginx.conf /etc/nginx/nginx.conf
# Default Nginx listens on 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
