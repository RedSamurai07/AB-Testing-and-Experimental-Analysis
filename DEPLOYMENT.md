# EC2 Deployment Guide

This guide details how to deploy the AB Testing Analysis Service directly on an AWS EC2 instance using Docker.

## Step 1: Launch and Setup EC2

1. Launch a **t2.micro** (or larger) instance with **Ubuntu 22.04 LTS**.
2. In **Security Groups**, allow:
   - SSH (Port 22)
   - FastAPI (Port 8000)
   - MLflow UI (Port 5000)
3. Connect to your instance via SSH.
   
   **On Windows (PowerShell):**
   ```powershell
   # Set permissions (Windows equivalent of chmod 400)
   icacls "ab_test-key.pem" /inheritance:r
   icacls "ab_test-key.pem" /grant:r "${env:USERNAME}:R"
   
   # Connect
   ssh -i "ab_test-key.pem" ubuntu@<EC2_PUBLIC_IP>
   ```

   **On Linux/Mac:**
   ```bash
   chmod 400 ab_test-key.pem
   ssh -i "ab_test-key.pem" ubuntu@<EC2_PUBLIC_IP>
   ```

## Step 2: Install Docker on EC2

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and log back in for group changes to take effect
```

## Step 3: Deploy the Service

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis.git
   cd AB-Testing-and-Experimental-Analysis
   ```

2. **Build and Run the Container:**
   ```bash
   # Build the image
   docker build -t ab-analysis-api .

   # Start the container
   # We map port 8000 for the API and port 5000 for MLflow
   docker run -d -p 8000:8000 -p 5000:5000 --name ab-service ab-analysis-api
   ```

## Step 4: Verification

Test the API from your local machine:

```bash
# Replace <EC2_PUBLIC_IP> with your instance's IP
curl http://<EC2_PUBLIC_IP>:8000/health
```

### Checking results in MLflow
Open your browser and navigate to:
`http://<EC2_PUBLIC_IP>:5000`

## CI Status
The build status of the main branch is tracked via GitHub Actions.
![Analysis Service CI](https://github.com/RedSamurai07/AB-Testing-and-Experimental-Analysis/actions/workflows/main.yml/badge.svg)
