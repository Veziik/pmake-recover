#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
FINALSTR=$NAME$COMMIT$DATE 
echo "starting program commit from $FINALSTR"
git add . 
git commit -m "$FINALSTR"
git push origin master
