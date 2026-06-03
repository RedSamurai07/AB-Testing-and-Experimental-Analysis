# 🚀 AWS EC2 Production Deployment Guide

This guide details the infrastructure configuration, container deployment strategy, and validation steps to host the A/B Testing Analysis Service on an AWS EC2 cloud instance using Docker.

---

## System Architecture Endpoints
* **Core API Layer (FastAPI):** `http://<EC2_PUBLIC_IP>:8000`
* **API Interactive Playground (Swagger UI):** `http://<EC2_PUBLIC_IP>:8000/docs`
* **Experiment Tracking Registry (MLflow UI):** `http://<EC2_PUBLIC_IP>:5000`

---

## Step 1: Launch and Configure EC2 Instance

1. **Provision Compute:** Launch an Amazon EC2 instance using **Ubuntu 22.04 LTS** (a `t2.micro` or `t3.small` instance is recommended).
2. **Configure Firewall / Security Groups:** Expose the minimum necessary ingress ports to authorize external traffic pipelines securely:
   * **SSH (Port 22):** For secure remote shell administration.
   * **FastAPI (Port 8000):** To handle client requests and statistical computation payloads.
   * **MLflow UI (Port 5000):** To monitor analytical run histories and model parameter logs.

### Establish Secure SSH Connection

#### On Windows (PowerShell):
```powershell
# Restrict file permissions to the current user (Windows equivalent of chmod 400)
icacls "ab_test-key.pem" /inheritance:r
icacls "ab_test-key.pem" /grant:r "${env:USERNAME}:R"

# Connect to the remote instance
ssh -i "ab_test-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

**On Linux/Mac:**
``` bash
# Set strict read-only permissions for the private key
chmod 400 ab_test-key.pem

# Connect to the remote instance
ssh -i "ab_test-key.pem" ubuntu@<EC2_PUBLIC_IP>
```
## Step 2: Install Container Runtime Environment

Once authenticated within the remote Ubuntu shell, initialize and configure the Docker engine:

```bash
# Update local package indexes
sudo apt-get update

# Install the standard Docker runtime
sudo apt-get install -y docker.io

# Enable the Docker daemon to automatically initialize on system boot
sudo systemctl start docker
sudo systemctl enable docker

# Add the default ubuntu user to the docker group to execute commands without sudo
sudo usermod -aG docker $USER

# CRITICAL: Terminate session and reconnect via SSH for group updates to take effect
exit
```

## Step 3: Deploy the Analysis Service

Reconnect to your EC2 instance and run the following deployment script to build the image layer and run the container with persistence guardrails:
``` bash
# 1. Clone the production source code from the repository
git clone [https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis.git](https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis.git)
cd AB-Testing-and-Experimental-Analysis

# 2. Build the Docker application image layer
docker build -t ab-analysis-api .

# 3. Instantiate the production container engine
# Maps runtime ports, ensures data persistence, and establishes crash auto-restart logic
docker run -d \
  -p 8000:8000 \
  -p 5000:5000 \
  -v mlflow_runs:/app/mlruns \
  --name ab-service \
  --restart unless-stopped \
  ab-analysis-api
```
💡 Production Enhancements Added:

--restart unless-stopped: Ensures the A/B testing service automatically reboots if the application crashes or the underlying EC2 server undergoes a hardware reboot.

-v mlflow_runs:/app/mlruns: Mounts a persistent named Docker volume so your tracked MLflow metadata and evaluation metrics survive container updates and deletions.

## Step 4: Infrastructure & Service Verification

**1. Health-Check Endpoint API Validation**

Test the baseline responsiveness of the FastAPI engine from your local machine terminal:

``` bash
curl http://<EC2_PUBLIC_IP>:8000/health
```

**2. Interactive Swagger API Playground**

FastAPI natively serves interactive OpenAPI documentation. You can test live statistical payloads directly through your web browser at:
``` bash
http://<EC2_PUBLIC_IP>:8000/docs
```
**3. Verify MLflow Experiment Logs**

To view evaluation parameters, time-series metrics, and visual comparison graphs of completed test variations, monitor the live portal at:
``` bash
http://<EC2_PUBLIC_IP>:5000
```

## CI/CD Pipeline Status
The operational integrity of the master codebase is continuously protected via automated integration testing gates:
![Analysis Service CI](https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis/actions/workflows/main.yml/badge.svg)
