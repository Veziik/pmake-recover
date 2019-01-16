#! /bin/bash 

printf "\nstarting program pull from git...\n"
git pull origin master #-m "pull from $NAME on $DATE"

printf "\nstarting file pull from git...\n"
cd files
git pull origin master #-m "pull from $NAME on $DATE"
cd ../