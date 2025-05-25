#!/bin/bash
# Загружаем переменные из .env
source .env

# Генерируем конфиг nginx
cat > mysite_nginx.conf << EOF
upstream django {
    server 127.0.0.1:8001;
}

server {
    listen 8000;
    server_name ${SERVER_IP};
    charset utf-8;
    client_max_body_size 75M;

    location /media {
        alias ${MEDIA_PATH};
    }
    
    location /static {
        alias ${STATIC_PATH};
    }

    location / {
        uwsgi_pass django;
        include /root/djangoapptest/Fasads_site/uwsgi_params;
    }
}
EOF

echo "Конфиг nginx создан!"
EOF