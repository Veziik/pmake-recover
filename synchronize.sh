#! /bin/bash 

printf "starting program pull from git...\n\n"
git pull origin master

printf "starting file pull from git...\n\n"
cd files
git pull origin master
cd ../