# opal-release-downloader
Obtain and verify all artifacts required to deploy OPAL

# Download Artifacts

## Environment 

Linux with:
* `/bin/bash` 
* Python3.9+ 
* pip
* Open internet connection


## Install

`pip install https://github.com/IM-USAF/opal-release-downloader`

## Usage

Runtime requirements must be obtained from OPAL developers prior to use:
* S3 bucket name in which OPAL artifacts reside, referred to as `<bucket name>`
* Release tag of available OPAL artifacts version, in the form of a date _YYYY.MM.DD_, referred to as `<release_tag>`

Download and validate artifacts:
* Navigate to an empty directory in which OPAL artifacts shall reside and do not navigate away from this directory for all remaining commands
* (if applicable) Ensure that the active environment is the one in which opal-release-downloader was installed
* Execute the download script and follow the prompts: `download_opal_artifacts`
* Execute the validation script: `validate_opal_artifacts`
* If all commands run without error, the artifact directory contains all of the artifacts required to deploy OPAL