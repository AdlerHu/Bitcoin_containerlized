#!/bin/sh

rm -f /var/lib/docker/volumes/htmls/_data/*

docker run --name crawler --net=container:bitcoin_mysql crawler >> /tmp/crawler.txt
docker run --name etl --net=container:bitcoin_mysql etl >> /tmp/etl.txt
docker run --name predict --net=container:bitcoin_mysql predict >> /tmp/predict.txt
docker run --name result --net=container:bitcoin_mysql result >> /tmp/result.txt
docker run --name charts --net=container:bitcoin_mysql -v htmls:/charts/templates/ charts >> /tmp/charts.txt
docker run --name webapp -d --net=host -v htmls:/webapp/templates/ webapp >> /tmp/webapp.txt

docker rm -f $(docker ps -qf status=exited)
