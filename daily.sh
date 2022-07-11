#!/bin/sh

rm -f /var/lib/docker/volumes/htmls/_data/*

docker run --name crawler --net=container:bitcoin-mysql-1 adlerhu/bitcoin_crawler >> /tmp/crawler.txt
docker run --name etl --net=container:bitcoin-mysql-1 adlerhu/bitcoin_etl >> /tmp/etl.txt
docker run --name predict --net=container:bitcoin-mysql-1 adlerhu/bitcoin_predict >> /tmp/predict.txt
docker run --name result --net=container:bitcoin-mysql-1 adlerhu/bitcoin_result >> /tmp/result.txt
docker run --name charts --net=container:bitcoin-mysql-1 -v htmls:/charts/templates/ adlerhu/bitcoin_charts >> /tmp/charts.txt
docker run --name webapp -d --net=host -v htmls:/webapp/templates/ adlerhu/bitcoin_webapp >> /tmp/webapp.txt

docker rm -f $(docker ps -qf status=exited)
