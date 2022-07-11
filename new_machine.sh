#!/bin/sh

apt-get update
apt-get upgrade -y

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
