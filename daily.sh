#!/bin/sh

rm -f /var/lib/docker/volumes/htmls/_data/*

docker run --name crawler --net=container:bitcoin-mysql-1 crawler:1.0.0 >> /tmp/crawler.txt
docker run --name etl --net=container:bitcoin-mysql-1 etl:1.0.0 >> /tmp/etl.txt
docker run --name predict --net=container:bitcoin-mysql-1 predict:1.0.0 >> /tmp/predict.txt
docker run --name result --net=container:bitcoin-mysql-1 result:1.0.0 >> /tmp/result.txt
docker run --name charts --net=container:bitcoin-mysql-1 -v htmls:/charts/templates/ charts:1.0.0 >> /tmp/charts.txt
docker run --name webapp -d --net=host -v htmls:/webapp/templates/ webapp:1.0.0 >> /tmp/webapp.txt

docker rm -f $(docker ps -qf status=exited)