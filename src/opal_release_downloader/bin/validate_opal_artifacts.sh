#!/bin/bash

set -e

_blue() {
  echo -e "\e[1;36m$@\n\e[0m"
}
_red() {
  echo -e "\e[1;31m$@\e[0m"
}
_green() {
  echo -e "\e[1;32m$@\n\e[0m"
}
_yellow() {
  echo -e "\e[1;33m$@\e[0m"
}

_check_dir_exists() {
  _yellow Checking directory $1 exists
  if [[ -d $1 ]]
  then
    _green Pass;
  else
    _red Directory $1 not found. Please ensure this script is run in the directory containing $1
    exit 1
  fi
}

_validate_checksums() {
  _yellow Validating checksums of .tar.bz2 files
  sum_file=$(ls | grep md5sums)
  md5sum -c $sum_file
  if [[ $? -eq 0 ]]
  then
    _green All files good
  else
    _red Looks like a file was incorrectly transferred, try copying the files over again
    exit 1
  fi
}

# It's important to only pass the opal-ops tarball through tar, else docker images will get fully unpacked (bad)
_unpack_ops_repo(){
  _yellow Unpacking opal-ops tarball
  if [[ -f opal-ops.tar.gz ]]
  then 
    tar -xzf opal-ops.tar.gz
    rm opal-ops.tar.gz
  else
    _red opal-ops tarball not found. Please place it in the images directory or check that all files were transferred correctly
    exit 1
  fi
}

_unzip_images(){
  _yellow Unzipping image tarballs. This may take a while ...
  files=$(ls | grep .bz2)
  for file in $files
  do
    echo $file
    bzip2 -d $file 
  done
}

_check_root_user() {
  if [[ $EUID -ne 0 ]]
  then
    _red "$0 is not running as root. Switch to root user before running script."
    exit 2
  else
    _green Pass
  fi
}

_blue Checking user is root

_check_root_user

_check_dir_exists images

_blue Entering images directory

cd images

_validate_checksums

_unzip_images

_unpack_ops_repo

_green All files unpacked, please run install-docker.sh and load images