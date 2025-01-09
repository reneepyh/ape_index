# Backend
FROM python:3.12-alpine AS backend
WORKDIR /app/backend

RUN apk add --no-cache build-base

COPY ./src/api /app/backend/src/api

COPY ./requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Frontend
FROM nginx:alpine AS frontend
WORKDIR /usr/share/nginx/html

COPY ./src/frontend /usr/share/nginx/html

COPY ./nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Combined
FROM python:3.12-alpine
RUN apk add --no-cache nginx

WORKDIR /app/backend

COPY --from=backend /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=backend /usr/local/bin /usr/local/bin
COPY --from=backend /app/backend /app/backend

COPY --from=frontend /usr/share/nginx/html /usr/share/nginx/html
COPY --from=frontend /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

ENV PATH="/usr/local/bin:$PATH"

EXPOSE 80
EXPOSE 8000

RUN mkdir -p /run/nginx && \
    chown -R nobody:nogroup /run/nginx

CMD sh -c "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"
