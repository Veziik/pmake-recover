#! /bin/bash
echo "1=$1"
echo "2=$2"
./pull.sh
./push.sh $1 $2
