#!/bin/sh

set -x -e -u

VIRTENV=$1
DIR=pypy3.5-5.9-beta-linux_x86_64-portable

wget -O $DIR.tar.bz2 https://bitbucket.org/squeaky/portable-pypy/downloads/pypy3.5-5.9-beta-linux_x86_64-portable.tar.bz2
tar xjf $DIR.tar.bz2
cd $DIR

wget -O virtualenv.py https://raw.github.com/pypa/virtualenv/15.1.0/virtualenv.py
./bin/pypy3 ./virtualenv.py --distribute $VIRTENV
