#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
FINALSTR=$NAME$COMMIT$DATE 

printf "starting program commit and push from $NAME on $DATE...\n\n"
git add --all
git commit -m "$FINALSTR"
git push origin master


printf "starting file commit and push from $NAME on $DATE...\n\n"
cd files
git add -all
git commit -m "$FINALSTR"
git push origin master
cd ../