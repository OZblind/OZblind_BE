 1. Nginx 공식 이미지를 기반으로 시작합니다.
FROM nginx:latest

# 2. 컨테이너 내부의 기본 Nginx 설정 파일을 삭제합니다.
RUN rm /etc/nginx/conf.d/default.conf

# 3. 우리가 만든 nginx.conf 파일을 컨테이너의 설정 폴더로 복사합니다.
COPY nginx.conf /etc/nginx/conf.d/