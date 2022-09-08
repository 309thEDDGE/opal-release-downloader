# opal-release-downloader
Obtain and verify all artifacts required to deploy OPAL

# Download OPAL Artifacts

## Environment 

### Linux

* Open internet connection
* docker 20.x.x
* Python3.9+ 
* pip
* On `PATH`: `bash`, `md5sum`, `tar`, `bzip2`


## Install

`pip install git+https://github.com/IM-USAF/opal-release-downloader.git`

## Usage

Runtime arguments: 

* must be obtained from OPAL developers prior to use:
* S3 bucket name in which OPAL artifacts reside, referred to as `<bucket name>`
* Release tag of available OPAL artifacts version, in the form of a date _YYYY.MM.DD_, referred to as `<release_tag>`

Download and validate artifacts:

* Navigate to an empty directory in which OPAL artifacts shall reside and do not navigate away from this directory for all remaining commands
* (if applicable) Ensure that the active environment is the one in which opal-release-downloader was installed
* View the help menu of the download script: `download_opal_artifacts -h`
* Execute the download script and pass arguments as described in the help menu: `download_opal_artifacts <bucket_name> ...`
* Do not use the flags `--no-docker` or `--no-rhel` unless you are an expert
* Some of the compressed images are several GBs in size. The download and verification process can take over an hour depending on internet connection and computer performance.
* If the command runs without error, the `opal_artifacts` directory contains all of the artifacts required to deploy OPAL

## Deployment

Acquire and validate artifacts:

* Move all artifacts within the `opal_artifacts` directory generated to the environment in which OPAL will be deployed
* Ensure that all artifacts exist inside a single directory
* Navigate to the artifact directory
* Execute the unpack and validation script: `/bin/bash ./unpack.sh`
* If there are no error messages and the script executes to completion, the artifacts are ready to be used to deploy OPAL
* If docker is not installed, proceed to the next section, otherwise skip it

Create a RHEL virtual machine:
* Use the rhel-*-x86_64-dvd.iso
* 

Install docker:

* Navigate to `docker` directory inside the directory in which all artifacts reside
* Switch to root user, one of: `sudo su -`, `su - root`, or `su -`
* Execute the docker installation script: `/bin/bash ./install-docker.sh`
* docker must be installed to deploy OPAL
* Change to the higher-level directory: `cd ..`

Load docker images:
* Remain root user if the "Install docker" step was followed, otherwise use one of the following to switch to root user: `sudo su -`, `su - root`, or `su -`
* Execute the load images script: `/bin/bash ./load-docker-images.sh`

Deploy OPAL via docker-compose:
