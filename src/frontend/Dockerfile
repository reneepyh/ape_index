FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remove default Nginx static files
RUN rm -rf ./*

COPY ./src/frontend .

RUN sed -i 's|window.BASE_URL = "";|window.BASE_URL = "'"${BASE_URL}"'";|g' index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
