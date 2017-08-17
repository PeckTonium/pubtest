#!/bin/sh
#set -e
#
# buildspec.sh
# We can't use buildspec files, because they must be at the root of the repo

echo "==============="
echo "path=$PATH"
which zip
echo
echo "About to ls /:"
#ls -l /
echo
echo "About to ls /usr:"
#ls -l /usr
echo
echo "About to ls /usr/bin:"
#ls -l /usr/bin
echo
echo "About to ls /usr/bin/zip:"
#ls -l /usr/bin/zip

#sudo apt-get install zip_3.0-11_amd64.deb
#sudo apt-get install zip_3.0-11_amd64
#sudo apt-get install ./zip_3.0-11_amd64.deb
#sudo apt-get install ./zip_3.0-11_amd64
#sudo apt-get install ./zip

more /etc/os-release
echo "About to 1"
#curl -o- http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip_3.0-8_amd64.deb | dpkg --install
echo "About to 2"
#sudo apt-get install http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip_3.0-8_amd64.deb
echo "About to 2.5"
#sudo apt-get install http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip*
echo "About to 3"
wget http://mirrors.kernel.org/ubuntu/pool/main/z/zip/zip_3.0-8_amd64.deb
ls -l 
sudo dpkg -i zip_3.0-8_amd64.deb
which zip


#sudo apt-get install lzip
#sudo apt-get install ./lzip_1.18-5_amd64.deb
#sudo apt-get install lzip
#sudo apt-get install xz-utils


#echo "About to curl -o- http://mirrors.kernel.org/ubuntu/pool/universe/l/lzip/lzip_1.18-5_amd64.deb | dpkg --install"
#curl -o- http://mirrors.kernel.org/ubuntu/pool/universe/l/lzip/lzip_1.18-5_amd64.deb | dpkg --install
echo "==============="

exit


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
$ZIPBINARY -9 --recurse-paths $TOPDIR/$ARTIFACT *
cd $TOPDIR
/usr/bin/zip --grow $ARTIFACT lambda.py

# post_build
# copy to s3
