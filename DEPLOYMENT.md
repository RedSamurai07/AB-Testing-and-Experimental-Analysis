# AWS Deployment Guide

This guide details how to deploy the AB Testing Analysis Service to AWS using Docker and AWS App Runner (for simplicity) or ECS.

## Prerequisites
- AWS CLI installed and configured.
- Docker installed locally.

## Step 1: Push Image to ECR

1. **Create ECR Repository:**
   ```bash
   aws ecr create-repository --repository-name ab-testing-api
   ```

2. **Login to ECR:**
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
   ```

3. **Build and Tag:**
   ```bash
   docker build -t ab-testing-api .
   docker tag ab-testing-api:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ab-testing-api:latest
   ```

4. **Push:**
   ```bash
   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ab-testing-api:latest
   ```

## Step 2: Deploy to AWS App Runner

1. Go to the **App Runner Console**.
2. Create **App Runner Service**.
3. Source: **Container Registry**.
4. Image Repository: Select your ECR repo and the `latest` tag.
5. Deployment Settings: **Automatic**.
6. Configuration:
   - Port: `8000`
   - Runtime: `Python` (Managed by Docker)
7. Create & Deploy.

## Step 3: Deployment Verification

Once App Runner provides a URL (e.g., `https://xxxx.region.awsapprunner.com`), test it:

```bash
curl https://xxxx.region.awsapprunner.com/health
```
