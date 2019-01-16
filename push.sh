#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
MESSAGE=""

if [ $# -eq 1 ]
then
	MESSAGE=": $1"
fi

FINALSTR=$NAME$COMMIT$DATE$MESSAGE


printf "\nstarting program commit and push from $NAME on $DATE..."
git add --all
git commit -m "$FINALSTR"
git push origin master
printf "\n"

printf "\nstarting file commit and push from $NAME on $DATE..."
cd files
git add --all
git commit -m "$FINALSTR"
git push origin master
cd ../
printf "\n"