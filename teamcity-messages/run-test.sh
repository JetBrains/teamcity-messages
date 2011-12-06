#!/bin/sh

cd test
export TEAMCITY_PROJECT_NAME=project_name

run() {
    NAME="$1"
    CMD="$2"
    
    $CMD 2>&1 | sed 's#File "[^"]*/#File "#g' | perl -pe 's/line \d+/line LINE/g' >test-$NAME.output.tmp 
    diff -Nru test-$NAME.output.gold test-$NAME.output.tmp
    if [ $? = 0 ]; then
        rm -f test-$NAME.output.tmp
    else
        echo "$NAME FAILED"
    fi
}

run unittest "python test-unittest.py"
run nose "nosetests test-nose.py"
