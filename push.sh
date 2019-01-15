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


printf "starting program commit and push from $NAME on $DATE...\n"
git add --all
git commit -m "$FINALSTR"
git push origin master
printf "\n"

printf "starting file commit and push from $NAME on $DATE...\n"
cd files
git add --all
git commit -m "$FINALSTR"
git push origin master
cd ../
printf "\n"