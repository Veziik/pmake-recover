#! /bin/bash 

printf "starting program pull from git"
git pull origin master

printf "starting file pull from git"
cd files
git pull origin master
cd ../