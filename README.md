
# opal-release-downloader

Download and verify all artifacts required to deploy OPAL. This README also includes the steps that must be followed to complete an OPAL deployment, broadly:

* [Download and verify artifacts](#download-and-validate-artifacts)
* [Prepare a Red Hat Enterprise Linux (RHEL) target with included ISO](#install-red-hat-linux)
* [Acquire](#acquire-artifacts), [extract, and verify](#validate-artifacts) artifacts within RHEL instance
* [Install docker](#install-docker) and [load OPAL docker images](#load-docker-images)
* [Configure](#configure-deployment) and [instantiate OPAL](#instantiate-opal)

## Environment 

* Open internet connection
* Python3.9+ with
  * pip
  * setuptools >= 43
* git

Installation and usage is OS-agnostic. We recommend that this package be installed and executed within a [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) environment. 

If you are using Windows and python was installed using the [python installer](https://www.python.org/downloads/windows/), the option to add python to the path automatically at install time must have been used. If that option was not used and python was manually added to the path, this script will likely not function as expected. Re-run the installer, choose the modify option, check the box to add python to the user path and complete the installation modification prior to the following steps. 

## Install

From within the python environment described in the [Environment](#environment) section, run the command:

`pip install git+https://github.com/309thEDDGE/opal-release-downloader.git`

_Note: On windows be sure to use_ `python -m pip install ...`.

This command will pull the source from github, then build and install the python package, including dependencies. It will place several scripts on your path in the active environment. Scripts are described in [Download and verify artifacts](#download-and-validate-artifacts).

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
* use the rhel-*-x86_64-dvd.iso found in the `rhel` directory
* Install in a VM (preferred) or bare metal
* Minimum installation options:
  * Memory:  
    * Disk Space: > 50GB  
    * RAM: > 8GB   
  * On first boot up using the `rhel-*-x86_64-dvd.iso`, when you get to the "Installation Summary Page" include the following selections.
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
* Expected directory structure:
  - docker/
  - images/
  - load-docker-images.sh
  - unpacker.sh
  - install-opal.sh

**Remaining sections describe commands or actions to be executed within RHEL.**

### Install OPAL

* Navigate to the artifact directory
* Execute the opal installer script: `sudo /bin/bash install-opal.sh`
  * This will validate artifact checksums one final time, install docker, unzip/load the images, and begin configuration
  * The configuration stage will ask several questions to tailor OPAL for your environment.
  * For future reference, note the value chosen for `<dns_base>`, the base name for the DNS which will be appended to the service name
* If there are no error messages and the script executes to completion, OPAL will be installed and ready to run without ssl.
  * To enable ssl, you will need to provide your own certificates.
  
### Add Certificates

Note: Certificates will not need to be generated when deploying locally.

Certificates will either need to be generated with a wildcard following the format: `*[.opal]<dns_base>`.

* Name the public and private certificates `tls.crt` and `tls.key`, respectively
* Place the certificates in `opal-ops/docker-compose/keycloak/certs/<deployment_label>`
* Additionally, copy the certificates to `opal-ops/docker-compose/jupyterhub/certs/selfsigned/` as `jhubssl.crt` and `jhubssl.key`

### Update etc/hosts
Update the `/etc/hosts` file based off instructions given when running the `install-opal` script. For example, when deploying locally, these additions need to be inserted into `/etc/hosts`.  
```
127.0.0.1 keycloak
127.0.0.1 minio
127.0.0.1 opal
```

### Instantiate OPAL

* Change directory to the location of the configured start script (script looks for `.env.secrets` in cwd): `cd ./opal-ops/docker-compose`
* Run the OPAL utility with the `start` option: `/bin/bash ./<deployment_label>_util.sh start`. This step builds several images, and may take a while on first run

## Verify Deployment

Follow the instructions in this section to verify that OPAL is running. These steps are only valid if all the steps in the [deployment](#opal-deployment) were completed successfully.

Depending on [configuration](#configure-deployment) URLs for various services will be in the form: `https://<service_name>[.opal]<dns_base>`.

If deploying locally and the following insertions were added to  `/etc/hosts`.  
```
127.0.0.1 keycloak
127.0.0.1 minio
127.0.0.1 opal
```
then the URLs associated with OPAL and Minio are:
```
https://opal
https://minio
```

Default credentials for local deployment. `User = opaluser, Password = opalpassword`
### Keycloak

* wip: execute keycloak health check script

### JupyterHub

* From within the VM, open the browser and navigate to `opal.<dns_base>`

### OPAL Catalog

* From the jupterlab interface, open a new terminal tab and run `/bin/bash /home/jovyan/opal/devops-software/test_all.bash`. If all tests pass, the catalog is working as intended.
* From the jupyterlab interface, click file -> Hub control panel. From the home page, click services -> Opal Catalog. This should redirect you to the catalog webpage. Click "Sign in with Jupyterhub", and the catalog should populate
