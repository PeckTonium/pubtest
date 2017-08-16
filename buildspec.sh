#!/bin/sh
set -e
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

echo "==============="
echo "==============="




echo "Starting buildspec.sh, have source_path=$source_path"
cd $source_path
echo $PATH
#export PATH="/usr/bin:/bin:$PATH"
ls -l /usr/bin/zip
TOPDIR=`pwd`
ARTIFACT=lambdapackage.zip
ZIPBINARY='sh -c "exec /usr/bin/zip"'
ZIPBINARY=/usr/bin/zip

# install
python2.7 -m pip install virtualenv
pip install --upgrade pip

# pre_build steps
virtualenv --python=python2.7 venv
venv/bin/pip install -r requirements.txt

# build
cd venv/lib/python2.7/site-packages
$ZIPBINARY -9 --recurse-paths $TOPDIR/$ARTIFACT *
cd $TOPDIR
/usr/bin/zip --grow $ARTIFACT lambda.py

# post_build
# copy to s3
