FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="londonappdeveloper.com"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chmod -R 755 /vol/web && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /vol/web

USER nginx

CMD ["/run.sh"]
