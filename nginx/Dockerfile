FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
RUN { \
      echo 'client_max_body_size 300m;'; \
    } > /etc/nginx/conf.d/my_proxy.conf
COPY nginx.conf /etc/nginx/conf.d