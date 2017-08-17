#!/bin/sh
set -e
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

echo "Starting buildspec.sh, have source_path=$source_path"
cd $source_path

TOPDIR=`pwd`
ARTIFACT=lambdapackage.zip
ZIPBINARY='sh -c "exec /usr/bin/zip"'
ZIPBINARY=/usr/bin/zip

# install
echo "Installing zip..."
wget http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip_3.0-8_amd64.deb
sudo dpkg -i zip_3.0-8_amd64.deb
echo "Installing virtualenv, upgrading pip"
python2.7 -m pip install virtualenv
pip install --upgrade pip

# pre_build steps
echo "Pre-build"
virtualenv --python=python2.7 venv
venv/bin/pip install -r requirements.txt

venv/bin/pip install semver
ARTIFACT=`sh ./nextbuildver.sh "$ARTIFACT"`

# build
echo "Build"
cd venv/lib/python2.7/site-packages
$ZIPBINARY --quiet -9 --recurse-paths $TOPDIR/$ARTIFACT *
$ZIPBINARY --show-files $TOPDIR/$ARTIFACT | tail
echo "== adding lambda"
cd $TOPDIR
$ZIPBINARY -9 $ARTIFACT lambda.py

echo "===="
$ZIPBINARY --show-files $ARTIFACT | tail
echo "===="

# post_build
echo "Post-Build"
# copy to s3
