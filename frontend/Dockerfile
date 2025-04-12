FROM nginx:alpine

# main-page.html dosyasını index.html olarak kopyala
COPY html/main-page.html /usr/share/nginx/html/index.html

# Diğer dosyaları kopyala
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY config.js /usr/share/nginx/html/