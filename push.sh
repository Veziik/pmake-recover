#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
MESSAGE1=""
MESSAGE2=""

if [ $# -eq 1 ]
then
	MESSAGE1=": $1"
fi

if [ $# -eq 2 ]
then
	MESSAGE2=": $2"
else
	MESSAGE2=": $1"
fi

FINALSTR1="$NAME$COMMIT$DATE$MESSAGE1"
FINALSTR2="$NAME$COMMIT$DATE$MESSAGE2"

printf "\nstarting program commit and push from $NAME on $DATE...\n"
printf "\nUsing commit message: $FINALSTR1 \n"
git add --all
git commit -m "$FINALSTR1"
git push origin master
printf "\n"

printf "\nstarting file commit and push from $NAME on $DATE...\n"
printf "\nUsing commit message: $FINALSTR2 \n"
cd files
git add --all
git commit -m "$FINALSTR2"
git push origin master
cd ../
printf "\n"