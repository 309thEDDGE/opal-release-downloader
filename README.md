# OPAL Release Downloader and Deployment Guide

## Overview

This guide provides step-by-step instructions to download, verify, and deploy OPAL.

## Prerequisites

### Environment Requirements

- **Operating System:** Ubuntu (via WSL or standalone Linux) or macOS
- **Internet Connection:** Required for downloading artifacts
- **Python:** Version 3.9+
  - Must include `pip` and `setuptools >= 43`
- **Git**: Installed and available in the system PATH
- **Docker & Docker Compose:** Installed and running

> **Note for Windows Users:** If using WSL, ensure you have installed WSL2 and Ubuntu. Install Docker Desktop with WSL integration enabled.

## Installation

### 1. Setup Python Environment

We recommend using a virtual environment:

```sh
python -m venv opal_env
source opal_env/bin/activate  # On Windows, use `opal_env\Scripts\activate`
```

### 2. Install OPAL Release Downloader

```sh
pip install git+https://github.com/309thEDDGE/opal-release-downloader.git
```

## Download and Verify OPAL Artifacts

1. **Navigate to an empty directory** where OPAL artifacts will be stored.
2. **Ensure you are in the correct Python environment.**
3. **View script options:**
   ```sh
   download_opal_artifacts -h
   ```
4. **Download artifacts:**
   ```sh
   download_opal_artifacts opal-deployment-artifacts
   ```
   This downloads and verifies required files into `opal_artifacts/`.

## OPAL Deployment

### 1. Copy Artifacts

Move `opal_artifacts/` to your target deployment machine.

### 2. Install OPAL

Run the installer script:

```sh
cd opal_artifacts
sudo /bin/bash install-opal.sh
```

The script will prompt for environment-specific details:

- **Deployment Name:** (e.g., `acceptance`, `cui`)
- **Banner Color:** Enter an HTML color (e.g., `Blue`)
- **Banner Text:** Network name or classification markings

### 3. Update Hosts File

If services do not resolve, modify your `/etc/hosts` file:

```sh
echo "127.0.0.1 minio.127.0.0.1.nip.io" | sudo tee -a /etc/hosts
echo "127.0.0.1 jupyterhub.127.0.0.1.nip.io" | sudo tee -a /etc/hosts
echo "127.0.0.1 keycloak.127.0.0.1.nip.io" | sudo tee -a /etc/hosts
```

> **For WSL Users:** Modify `/etc/hosts` inside WSL, not Windows.

### 4. Start OPAL Services

```sh
cd opal-ops/docker-compose
/bin/bash ./<deployment_label>_util.sh start
```

### 5. Verify Deployment

Access services in a browser:

- **OPAL:** [https://opal](https://opal)
- **Minio:** [https://minio](https://minio)
- **JupyterHub:** `opal.<dns_base>` (replace `<dns_base>` with your configuration)

## Daily Usage: Starting OPAL After Installation

Once OPAL is installed, you can start it for daily use by running:

```sh
cd opal-ops/docker-compose
/bin/bash ./<deployment_label>_util.sh start
```

If OPAL is already running, you may restart services with:

```sh
/bin/bash ./<deployment_label>_util.sh restart
```

To stop OPAL services:

```sh
/bin/bash ./<deployment_label>_util.sh stop
```

## Troubleshooting

### Stop & Remove Running Containers

```sh
docker ps -q | xargs docker stop  # Stop all running containers
docker system prune -af           # Remove unused containers, images, and volumes
```

### Restart Docker

```sh
sudo systemctl restart docker
```

### Check Logs

```sh
docker logs <container_id>
```

---