#! /bin/bash 
NAME=`hostname` 
DATE=`date`
COMMIT=" commit " 
FINALSTR=$NAME$COMMIT$DATE 
echo FINALSTR
git add . 
git commit -m " \' $FINALSTR \'"
git push origin master
