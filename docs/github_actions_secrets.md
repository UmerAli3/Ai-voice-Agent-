# GitHub Actions CI/CD Deployment & Secrets Configuration Guide

This document details the configuration of the automated CI/CD pipeline using **GitHub Actions**, container registry publication via **GHCR**, remote deployment over **SSH**, and zero-downtime rollback strategies.

---

## 1. CI/CD Pipeline Architecture Overview

The pipeline (`.github/workflows/deploy.yml`) consists of three automated stages:

1. **Linting & Unit Testing (`test`)**:
   - Spins up an ephemeral PostgreSQL 16 service container.
   - Installs dependencies and runs `ruff check src/`.
   - Executes `pytest` unit test suite against active database schema.

2. **Docker Build & Registry Push (`build-and-push`)**:
   - Uses `docker/build-push-action` with Docker Buildx caching.
   - Builds production multi-stage `Dockerfile`.
   - Tags and pushes images to GitHub Container Registry (`ghcr.io`).

3. **SSH Remote Deployment & Verification (`deploy`)**:
   - Connects to target production Linux server via SSH.
   - Executes `docker compose pull` and `docker compose up -d --build`.
   - Runs an automated 10-attempt post-deployment HTTP health check (`http://localhost:8000/health`).
   - Automatically triggers a rollback if health check fails.

---

## 2. Required GitHub Repository Secrets

Configure the following secrets in your GitHub repository (**Settings** -> **Secrets and variables** -> **Actions**):

| Secret Name | Description | Example / Format |
| :--- | :--- | :--- |
| `PROD_SERVER_HOST` | IPv4 address or hostname of production server | `203.0.113.50` or `api.internexus.tech` |
| `PROD_SERVER_USER` | Linux SSH username on server | `ubuntu` or `deploy` |
| `PROD_SSH_PRIVATE_KEY` | Ed25519 or RSA OpenSSH private key | `-----BEGIN OPENSSH PRIVATE KEY----- ...` |
| `PROD_SERVER_PORT` | SSH port (Optional, default `22`) | `22` |

> **Note**: `GITHUB_TOKEN` is automatically created and injected by GitHub Actions to authenticate with GHCR (`ghcr.io`).

---

## 3. SSH Key Generation & Server Setup

### Step 1: Generate SSH Keypair on your local machine
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy@internexus.tech" -f ~/.ssh/github_deploy_key
```

### Step 2: Add Public Key to Production Server
Copy the generated `.pub` key to `/home/ubuntu/.ssh/authorized_keys` on your production server:
```bash
cat ~/.ssh/github_deploy_key.pub | ssh ubuntu@203.0.113.50 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Step 3: Add Private Key to GitHub Secrets
Copy the full content of `~/.ssh/github_deploy_key` into the `PROD_SSH_PRIVATE_KEY` secret in GitHub.

---

## 4. Initial Server Setup Instructions

On your production server, prepare the deployment directory before running your first workflow:

```bash
sudo mkdir -p /opt/healthcare-voice-agent
sudo chown -R ubuntu:ubuntu /opt/healthcare-voice-agent
cd /opt/healthcare-voice-agent

# Clone or copy docker-compose.yml, nginx, prometheus, grafana and .env
# Ensure .env is populated with production database credentials and secrets:
cp .env.example .env
```

---

## 5. Automated Healthcheck & Rollback Strategy

- **Automated Rollback**: If `POST /health` fails 10 consecutive times following container launch, `deploy.yml` aborts and rolls back to the previously functioning container instance.
- **Manual Rollback**: Go to GitHub Actions -> **Manual / Emergency Rollback** -> **Run workflow**, specify the desired target commit SHA or image tag (e.g. `latest` or `sha-a1b2c3d`), and click **Run**.
