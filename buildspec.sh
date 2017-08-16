#!/bin/sh
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

cd $source_path

TOPDIR=`pwd`
ARTIFACT=lambdapackage.zip

# install

# pre_build steps
virtualenv --python=python2.7 --no-setuptools --no-wheel venv
venv/bin/pip install -r requirements.txt

# build
cd venv/lib/python2.7/site-packages
zip -9 --recurse-paths $TOPDIR/$ARTIFACT *
cd $TOPDIR
zip --grow $ARTIFACT lambda.py

# post_build
# copy to s3
