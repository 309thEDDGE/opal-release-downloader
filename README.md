# opal-release-downloader

Download and verify all artifacts required to deploy OPAL. This README also includes the steps that must be followed to complete an OPAL deployment, broadly:

* [Download and verify artifacts](#download-and-validate-artifacts)
* [Prepare a Red Hat Enterprise Linux (RHEL) target with included ISO](#install-red-hat-linux)
* [Acquire](#acquire-artifacts), [extract, and verify](#validate-artifacts) artifacts within RHEL instance
* [Install docker](#install-docker) and [load OPAL docker images](#load-docker-images)
* [Configure](#configure-deployment) and [instantiate OPAL](#instantiate-opal)

## Environment 

* Open internet connection
* docker 20.x.x
* Python3.9+ 
* pip

Installation and usage is OS-agnostic. We recommend that this package be installed and executed within a [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) environment. 

If you are using Windows and python was installed using the [python installer](https://www.python.org/downloads/windows/), the option to add python to the path automatically at install time must have been used. If that option was not used and python was manually added to the path this script will likely not function as expected. Re-run the installer, choose the modify option, check the box to add python to the user path and complete the installation modification prior to the following steps. 

## Install

From within the python environment described in the [Environment](#environment) section, run the command:

`pip install git+https://github.com/IM-USAF/opal-release-downloader.git`

## Usage

### Runtime arguments: 

* must be obtained from OPAL developers prior to use
* S3 bucket name in which OPAL artifacts reside, referred to as `<bucket name>`
* Release tag of available OPAL artifacts version, in the form of a date _YYYY.MM.DD_, referred to as `<release_tag>`

### Download and validate artifacts:

* Navigate to an empty directory in which OPAL artifacts shall reside
* (if applicable) Ensure that the active environment is the one in which opal-release-downloader was installed
* View the help menu of the download script: `download_opal_artifacts -h`
* Execute the download script and pass arguments as described in the help menu: `download_opal_artifacts <bucket_name> ...`
* `<bucket_name>` can be omitted to automatically grab the latest tag
* See `list_opal_artifacts -h` to view available tags
* Do not use the flags `--no-docker` or `--no-rhel` unless you are an expert
* Some of the compressed images are several GBs in size. The download and verification process can take over an hour depending on internet connection and computer performance.
* If the command runs without error, the `opal_artifacts` directory contains all of the artifacts required to deploy OPAL

## OPAL Deployment

### Install Red Hat Linux

* Copy all artifacts from the `opal_artifacts` directory (previous section) to the destination network
* Use the rhel-*-x86_64-dvd.iso found in the `rhel` directory
* Install in a VM (preferred) or bare metal
* Minimum installation options:
  * "Software Selection":
    * "Base Environment": Server with GUI
    * "Additional software for Selected Environment":
      * Windows File Server
      * Guest Agents
      * Network File System Client
      * Development Tools
      * Headless Management
  * "Root Password":
    * Set a root password
  * "Add User":
    * Create an administrator user account

### Acquire Artifacts

* Copy all artifacts into a directory on the RHEL file system
* Ensure that all artifacts exist inside a single directory

**Remaining sections describe commands or actions to be executed within RHEL.**

### Validate Artifacts

* Navigate to the artifact directory
* Execute the unpack and validation script: `/bin/bash ./unpack.sh`
* If there are no error messages and the script executes to completion, the artifacts are ready to be used to deploy OPAL

### Execute Commands as Root User

* Switch to root user: `sudo su -`
* **All remaining steps shall be executed as root user**

### Install Docker

* Navigate to `docker` directory inside the directory in which all artifacts reside: `cd docker`
* Execute the docker installation script: `/bin/bash ./install-docker.sh`
* Change to the higher-level directory: `cd ..`

### Load Docker Images

* Execute the load images script: `/bin/bash ./load-docker-images.sh`

### Configure Deployment

* Execute configuration script: `/bin/bash ./images/opal-ops/docker-compose/configuration/new_deployment.bash`
* Assign a label (`<deployment_label>`) to the deployment configuration, via on-screen prompts
* Localhost deployment option is for testing on a stand-alone machine and not intended for production -- _in beta_
* For future reference, note the value chosen for `<dns_base>`, the base name for the DNS which will be appended to the service name
* On completion, a new script will be created that calls `docker-compose` with the correct configuration file: `start_<deployment_label>.sh`

### Instantiate OPAL

* Change directory to the location of the configured start script (script looks for `.env.secrets` in cwd): `cd ./images/opal-ops/docker-compose`
* Execute the configured start script: `/bin/bash ./start_<deployment_label>.sh`

## Verify Deployment

Follow the instructions in this section to verify that OPAL is running. These steps are only valid if all the steps in the [deployment](#opal-deployment) were completed successfully.

Depending on [configuration](#configure-deployment) URLs for various services will be in the form: `https://<service_name>[.opal]<dns_base>`. 

### Keycloak

* wip: execute keycloak health check script

### JupyterHub

* From within the VM, open the browser and navigate to the URL with `<service_name> = jupyterlab
* wip: execute all tests
* Is this sufficient to consider that catalog-fe/be, minio, are functioning?