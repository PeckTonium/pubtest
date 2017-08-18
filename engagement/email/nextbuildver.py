#!/usr/bin/env python
'''
nextbuildver.py

Find the next build version number and either return it if there are no
arguments passed in, or else insert/append it to the string passed in
and return that.  If a string is passed in, it is used instead of the env
var artifact_name.  Note that whatever value is used for the artifact_name,
it must not contain a version number, as the new version will be inserted.

The string passed in is expected to be a file name, ending with a dot
extension.  The next version number will be inserted before the extension
or else appended if there is no extension.  Either way, the version will be
preceeded by an underscore.  For example:
  abc -> abc_4.2.4
  abc.sh -> abc_4.2.4.sh

There must be certain environment variables present for this script to operate:

  artifact_name - the base filename to calculate the build number for
  s3_bucket - the bucket to find existing artifacts (to find the latest one)
'''
import os
import re
import sys

import boto3
import semver



##### Verify arguments and settings

if len(sys.argv) > 2:
  print "Error: at most one argument is allowed"
  exit(1)
elif len(sys.argv) == 2:
  base_fname = sys.argv[1]
else:
  base_fname=""

print "Have base_fname=%s" % (base_fname if "base_fname" in dir() else "")
if base_fname:
  artifact_name = base_fname
else:
  if os.environ.has_key("artifact_name"):
    artifact_name = os.environ.get('artifact_name')
  else:
    print "Error: env var \"artifact_name\" missing"
    exit(1)

if os.environ.has_key("s3_bucket"):
  s3_bucket_name = os.environ.get('s3_bucket')
else:
  print "Error: env var \"s3_bucket\" missing"
  exit(1)

print "Have bucket=%s and artifact=%s" % (s3_bucket_name, artifact_name)

###### Check bucket name

s3Client = boto3.client('s3')

response = s3Client.list_buckets()
buckets = [bucket['Name'] for bucket in response['Buckets']]

if s3_bucket_name not in buckets:
  print "Error: env var \"s3_bucket\" has an invalid value (%s)" % s3_bucket_name
  exit(1)



s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
  for key in bucket.objects.all():
    print "key=%s" % key.key



bucket = s3.Bucket("s3_bucket_name")
obj_iterator = bucket.objects.filter(
  Prefix="artifact_name"
  )

#print "Got back object list: %s" % (obj for obj in obj_iterator)
for obj in obj_iterator:
  print "Got object: %s" % obj

