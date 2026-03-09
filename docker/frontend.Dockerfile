FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json ./package.json
COPY frontend/package-lock.json ./package-lock.json
RUN npm install
COPY frontend ./
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
