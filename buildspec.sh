#!/bin/sh
#set -e
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

wget http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip_3.0-8_amd64.deb
ls -l 
#sudo dpkg -i zip_3.0-8_amd64.deb
which zip
sudo apt-cache search zip
sudo apt-get install zip
which zip

echo "==============="



echo "Starting buildspec.sh, have source_path=$source_path"
cd $source_path

TOPDIR=`pwd`
ARTIFACT=lambdapackage.zip
ZIPBINARY='sh -c "exec /usr/bin/zip"'
ZIPBINARY=/usr/bin/zip

# install
python2.7 -m pip install virtualenv
pip install --upgrade pip

echo "===="

# pre_build steps
virtualenv --python=python2.7 venv
venv/bin/pip install -r requirements.txt

# build
cd venv/lib/python2.7/site-packages
$ZIPBINARY --quiet ---display-dots 9 --recurse-paths --output-file $TOPDIR/$ARTIFACT *
cd $TOPDIR
$ZIPBINARY  -9 $ARTIFACT lambda.py

echo "===="
ls -l
echo "===="
$ZIPBINARY --show-files $ARTIFACT
echo "===="
# post_build
# copy to s3
