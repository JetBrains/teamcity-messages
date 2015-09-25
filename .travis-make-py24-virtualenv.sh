#!/bin/sh

### Original script copy-pasted from numpy 1.7.x branch

VIRTENV=$1
set -x
set -e
wget -O Python-2.4.6.tar.bz2 http://www.python.org/ftp/python/2.4.6/Python-2.4.6.tar.bz2
tar xjf Python-2.4.6.tar.bz2
cd Python-2.4.6
cat >setup.cfg <<EOF
[build_ext]
library_dirs=/usr/lib/$(dpkg-architecture -qDEB_HOST_MULTIARCH)/
EOF
./configure --prefix=$PWD/install
make
make install
# Install an old version of virtualenv that supports python 2.4:
wget -O virtualenv.py https://raw.github.com/pypa/virtualenv/1.3.4/virtualenv.py
# And this is the last version of pip to support python 2.4. If
# there's a file matching "^pip-.*(zip|tar.gz|tar.bz2|tgz|tbz)$" in
# the current directory then virtualenv will take that as the pip
# source distribution to install
wget -O pip-1.1.tar.gz http://pypi.python.org/packages/source/p/pip/pip-1.1.tar.gz
install/bin/python2.4 ./virtualenv.py $VIRTENV
