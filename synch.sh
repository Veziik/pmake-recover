#! /bin/bash 
NAME=`hostname` 
DATE=`date`

printf "starting program pull from git...\n\n"
git pull origin master -m "pull from $NAME on $DATE"

printf "starting file pull from git...\n\n"
cd files
git pull origin master -m "pull from $NAME on $DATE"
cd ../