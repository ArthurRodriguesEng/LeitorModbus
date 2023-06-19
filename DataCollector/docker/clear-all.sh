#!/bin/sh

LIST=$(docker ps -aq)
if [ -n "$LIST" ]; then
    echo "List: $LIST"
    docker rm -f $LIST
fi

LIST=$(docker images -q)
if [ -n "$LIST" ]; then
    docker rmi -f $LIST
fi

