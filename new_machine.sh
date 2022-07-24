#!/bin/sh

apt-get update
apt-get upgrade -y

# sset hostname
echo "linode" > /etc/hostname

# install Docker
apt-get install  -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
	
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update  
apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# create docker volume
docker volume create mysql
docker volume create htmls

# pull needed images
docker pull adlerhu/bitcoin_crawler
docker pull adlerhu/bitcoin_etl
docker pull adlerhu/bitcoin_predict
docker pull adlerhu/bitcoin_result
docker pull adlerhu/bitcoin_charts
docker pull adlerhu/bitcoin_webapp

# daily job
touch /root/daily.sh
echo "#!/bin/sh

rm -f /var/lib/docker/volumes/htmls/_data/*
docker run --name crawler --net=container:bitcoin_mysql adlerhu/bitcoin_crawler
docker run --name etl --net=container:bitcoin_mysql adlerhu/bitcoin_etl
docker run --name predict --net=container:bitcoin_mysql adlerhu/bitcoin_predict
docker run --name result --net=container:bitcoin_mysql adlerhu/bitcoin_result
docker run --name charts --net=container:bitcoin_mysql -v htmls:/charts/templates/ adlerhu/bitcoin_charts
docker run --name webapp -d --net=host -v htmls:/webapp/templates/ adlerhu/bitcoin_webapp
docker container prune " >> /root/daily.sh

# mysql
touch /root/mysql.yml
echo "version: '3.3'
services:
  mysql:
      image: mysql:8.0
      container_name: bitcoin_mysql
      command: mysqld --default-authentication-plugin=mysql_native_password
      ports: 
          - 3306:3306
      environment: 
          MYSQL_DATABASE: mydb
          MYSQL_USER: user
          MYSQL_PASSWORD: hl4su3ao4
          MYSQL_ROOT_PASSWORD: hl4su3ao4
      volumes:
          - mysql:/var/lib/mysql
      networks:
          - dev
  phpmyadmin:
      image: phpmyadmin/phpmyadmin:5.1.0
      container_name: bitcoin_phphmyadmin
      links: 
          - mysql:db
      ports:
          - 8000:80
      depends_on:
        - mysql
      networks:
          - dev
     
networks:
  dev:
volumes:
  mysql:
    external: true" >> /root/mysql.yml

docker compose -f /root/mysql.yml up -d
