#!/bin/sh

docker run --name crawler --net=container:bitcoin_mysql crawler:1.0.0
docker run --name etl --net=container:bitcoin_mysql etl:1.0.0
docker run --name predict --net=container:bitcoin_mysql predict:1.0.0
docker run --name result --net=container:bitcoin_mysql result:1.0.0
docker run --name charts --net=container:bitcoin_mysql -v htmls:/charts/templates/ charts:1.0.0
docker run --name webapp -d --net=host -v htmls:/webapp/templates/ webapp:1.0.0

docker container prune -f
