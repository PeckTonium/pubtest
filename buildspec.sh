#!/bin/sh
set -e
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

echo "==============="
echo "/usr:"
ls -C /usr
echo
echo "/usr/bin:"
ls -C /usr/bin
echo
echo "bin:"
ls -C /bin
echo
echo "/sbin:"
ls -C /sbin
echo "==============="




echo "Starting buildspec.sh, have source_path=$source_path"
cd $source_path

TOPDIR=`pwd`
ARTIFACT=lambdapackage.zip

# install
python2.7 -m pip install virtualenv
pip install --upgrade pip

# pre_build steps
virtualenv --python=python2.7 venv
venv/bin/pip install -r requirements.txt

# build
cd venv/lib/python2.7/site-packages
/usr/bin/zip -9 --recurse-paths $TOPDIR/$ARTIFACT *
cd $TOPDIR
/usr/bin/zip --grow $ARTIFACT lambda.py

# post_build
# copy to s3
