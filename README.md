# opal-release-downloader
Obtain and verify all artifacts required to deploy OPAL

# Download OPAL Artifacts

## Environment 

### Linux

* Open internet connection
* Python3.9+ 
* pip
* On `PATH`: `bash`, `md5sum`, `tar`, `bzip2`


## Install

`pip install git+https://github.com/IM-USAF/opal-release-downloader.git`

## Usage

Runtime requirements must be obtained from OPAL developers prior to use:

* S3 bucket name in which OPAL artifacts reside, referred to as `<bucket name>`
* Release tag of available OPAL artifacts version, in the form of a date _YYYY.MM.DD_, referred to as `<release_tag>`

Download and validate artifacts:

* Navigate to an empty directory in which OPAL artifacts shall reside and do not navigate away from this directory for all remaining commands
* (if applicable) Ensure that the active environment is the one in which opal-release-downloader was installed
* View the help menu of the download script: `download_opal_artifacts -h`
* Execute the download script and pass arguments as described in the help menu: `download_opal_artifacts <bucket_name> ...`
* Some of the compressed images are several GBs in size. The download and verification process can take over an hour depending on internet connection and compute performance.
* If the command runs without error, the artifact directory contains all of the artifacts required to deploy OPAL

Prepare for deployment:

* Move all artifacts to the environment in which OPAL will be deployed
* Execute the unpack and validation script, which : `/bin/bash unpack.sh`
* If there are no error messages and the script executes to completion, the artifacts are ready to be used to deploy OPAL
