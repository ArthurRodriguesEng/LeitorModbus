#!/bin/sh

SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")
cd $DIR

mkdir -p ../pgdata ../mgdata

docker compose up --build -d
echo
sleep 5
docker compose ps
echo
