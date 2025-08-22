# 1. Nginx 공식 이미지를 기반으로 시작합니다.
FROM nginx:latest

COPY nginx.conf /etc/nginx/templates/default.conf

CMD ["nginx", "-g", "daemon off;"]