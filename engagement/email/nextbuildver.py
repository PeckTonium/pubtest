#!/usr/bin/env python
'''
nextbuildver.py

Print the next build version number of the specified build artifact.

The artifact_name will be used as the basis to find the correct item to version.  The last dot
will be used as the file extension, which will follow the version number in the final file.

For example:
  abc.tgz -> abc_0.0.5-rc.4.tgz
  a.b -> a_0.0.5-rc.4.b
Note: the artifact_name must have the version following the last underscore, i.e a_this_1.2.3.tgz

The bucket_dir directory in the bucket_name s3 bucket will be searched for all files
prefixed with artifact_name ($artifact_name*, without the extension if present).  The highest version
found will be incremented and printed to stdout

If --major is present, then the major version will be incremented and the rest will be set to zero
  with a new prerelease version
If --minor is present, then the minor version will be incremented and the rest will be set to zero
  with a new prerelease version
If --patch is present, then the patch version will be incremented and the rest will be set to zero
  with a new prerelease version
if --release is present, then the pre-release and build versions will be removed
'''

import argparse
import os
import re
import sys

import boto3
import botocore
import semver

parser = argparse.ArgumentParser(description='Find next version number')
parser.add_argument('--artifact_name', required=True,
                    help='the base of the artifact to version')
parser.add_argument('--bucket_name', required=True,
                    help='the name of the s3 bucket that the artifacts are in')
parser.add_argument('--bucket_dir', required=True,
                    help='the directory inside the s3 bucket where artifacts are')
parser.add_argument('--major', action='store_true')
parser.add_argument('--minor', action='store_true')
parser.add_argument('--patch', action='store_true')
parser.add_argument('--release', action='store_true')
args = parser.parse_args()

###### Check parameter values

s3_client = boto3.client('s3')
try:
  s3_client.head_bucket(Bucket=args.bucket_name)
except botocore.exceptions.ClientError as clerr:
  print "Error: \"bucket_name\" has an invalid value (%s)" % args.bucket_name
  exit(1)
  
s3 = boto3.resource('s3')

ext_index = args.artifact_name.rfind(".")
if ext_index != -1:
  file_extension = args.artifact_name[ext_index:]
  file_name = args.artifact_name[:ext_index]
  if not file_name:
    print "Error: No base file name (without extension) specified in artifact_name (%s)" \
      % args.artifact_name
    exit(1)
else:
  print "Error: No file extension found in the artifact_name (%s)" % args.artifact_name
  exit(1)

# Go find what versions already exist

artifact_prefix=args.bucket_dir + "/" + file_name
bucket = s3.Bucket(args.bucket_name)
obj_iterator = bucket.objects.filter(Prefix=artifact_prefix)
item_names = sorted([x.key for x in obj_iterator])

if not len(item_names):
  # New file to begin versioning
  new_ver = semver.format_version(0, 0, 1)
  new_ver = semver.bump_prerelease(new_ver)
  print new_ver
  exit(0)

ver_index = item_names[-1].rfind("_")
highest_existing_ver= item_names[-1][ver_index:]

if item_names[-1][:ver_index] != artifact_prefix:
  print "Error: Found no versioned files based on %s" % artifact_prefix
  exit(1)

if highest_existing_ver.startswith("_"):
  highest_existing_ver = highest_existing_ver[1:]
else:
  print "Have highest_existing_ver=%s" % highest_existing_ver
  print "Error: the highest existing version number doesn't start with \"_\" (%s)" % item_names[-1]
  exit(1)

# Remove the extension
ext_index = highest_existing_ver.rfind(file_extension)
if ext_index < 1:
  print "Error: The extension in the artifact_name was not found on any versioned artifacts " \
    "(%s not in %s)" % (file_extension, item_names[-1])
  exit(1)
else:
  highest_existing_ver = highest_existing_ver[:ext_index]

try:
  parsed = dict(semver.parse(highest_existing_ver))
  if args.release:
    new_ver = semver.format_version(parsed['major'], parsed['minor'], parsed['patch'])
  elif args.major:
    new_ver = semver.bump_major(highest_existing_ver)
    new_ver = semver.bump_prerelease(new_ver)
  elif args.minor:
    new_ver = semver.bump_minor(highest_existing_ver)
    new_ver = semver.bump_prerelease(new_ver)
  elif args.patch:
    new_ver = semver.bump_patch(highest_existing_ver)
    new_ver = semver.bump_prerelease(new_ver)
  else:
    if not parsed['prerelease']:
      # If the last version has no prerelease version (was a real release), the next one will
      new_ver = semver.bump_patch(highest_existing_ver)
      new_ver = semver.bump_prerelease(new_ver)
    else:
      new_ver = semver.bump_prerelease(highest_existing_ver)
except ValueError as valerr:
  print "Error: an error occurred working with version number on file %s: %s" % (item_names[-1], valerr)
  exit(1)

print new_ver
