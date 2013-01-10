#!/bin/sh

set -e

tmp=`mktemp -d`
trap "rm -rf $tmp" EXIT

prepare_nose() {
    easy_install -q "$dcache/nose-1.2.1.tar.gz"
}

prepare_pytest() {
    easy_install -q "$dcache/py-1.4.12.zip"
    easy_install -q "$dcache/pytest-2.3.4.zip"
    rm -rf test/__pycache__
}

run() {
    name="$1"
    prereq="$2"
    cmd="$3"

    venv="$tmp/$name"

    rm -rf "$venv"
    virtualenv -q --never-download --distribute --no-site-packages "$venv"

    (
    . "$venv/bin/activate"
    easy_install -q "$egg"
    [ -z "$prereq" ] || $prereq

    cd test

    # Emulate running under TeamCity
    export TEAMCITY_PROJECT_NAME=project_name

    $cmd 2>&1 | \
        perl -pe 's/File "[^"]+"/File "FILE"/g' | \
        perl -pe 's/passed in \d+\.\d+ seconds/passed in X.XX seconds/g' | \
        perl -pe 's/^platform .+$/platform SPEC/' | \
        sed 's#instance at 0x.*>#instance at 0x????????>#' | \
        perl -pe 's/line \d+/line LINE/g' \
        >test-$name.output.tmp

    diff -Nru test-$name.output.gold test-$name.output.tmp
    if [ $? = 0 ]; then
        rm -f test-$name.output.tmp
    else
        echo "$name FAILED"
    fi
    )
}

rm -rf dist
python setup.py -q bdist_egg
egg=$(echo $(pwd)/dist/*.egg)
test -f "$egg"

dcache="$(pwd)/test_support"

run unittest "" "python test-unittest.py"
run nose "prepare_nose" "nosetests test-nose.py"
run pytest "prepare_pytest" "py.test --teamcity test-pytest.py"
