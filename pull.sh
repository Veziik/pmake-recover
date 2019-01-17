#! /bin/bash 

printf "\nstarting program pull from git...\n"
<<<<<<< HEAD
git pull origin master #-m "pull from $NAME on $DATE"
=======
git pull origin master 
>>>>>>> ed3c12985d855270bf990c56d85d5c47f94ff636

printf "\nstarting file pull from git...\n"
cd files
git pull origin master 
cd ../