#!/bin/sh
#set -e
#
# nextbuildver.sh
# Find the next build version number and either return it if no arguments
# were passed in, or insert/append it to the filename passed in
# If the argument passed in has a dot in it, the version will be inserted
# before the dot with a leading underscore
# eg: abc -> abc_4.2.4   or a.sh -> a_4.2.4.sh
#
# Expects one environment variable to exist:
#   artifact_name - the base filename to calculate the build number for
#   s3_bucket - the bucket where artifacts reside (to see latest one)

echo "Starting nextbuildver.sh"

if [[ $# > 2 ]]; then
  echo "Error: There must be at most one argument.  If present, it must \
    be a filename to be modified"
  exit 1
fi

if [[ -n "$1" ]]; then
  fname="$1"
  echo "got filename=$fname"
else
  if [[ -z "$1" ]]; then
    echo "got -z \$1"
  fi
fi

if [[ -z "$artifact_name" ]]; then
  echo "Error: Missing environment variable \$artifact_name"
  exit 1
fi

if [[ -z "$s3_bucket" ]]; then
  echo "Error: Missing environment variable \$s3_bucket"
  exit 1
fi

