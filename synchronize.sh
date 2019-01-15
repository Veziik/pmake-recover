#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
FINALSTR=$NAME$COMMIT$DATE 

printf "starting program commit from $NAME on $DATE\n\n"
git add . 
git commit -m "$FINALSTR"
git push origin master
