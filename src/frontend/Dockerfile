FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remove default Nginx static files
RUN rm -rf ./*

COPY ./src/frontend .

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
