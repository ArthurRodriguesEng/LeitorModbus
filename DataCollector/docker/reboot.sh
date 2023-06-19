#!/bin/sh

SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")
cd $DIR

sh down.sh
sh run.sh

