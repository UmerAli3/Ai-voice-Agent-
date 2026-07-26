# Production Server Deployment Guide (Ubuntu 22.04/24.04 LTS)

**Target Server IP**: `68.233.98.166`  
**Domain Names**: `api.internexus.tech`, `grafana.internexus.tech`, `prometheus.internexus.tech`  
**Operating System**: Ubuntu 22.04 LTS / 24.04 LTS

---

## 1. Initial Server Setup & Package Updates

SSH into the target server:

```bash
ssh ubuntu@68.233.98.166
```

Update system package indices and upgrade existing packages to their latest stable releases:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git ufw htop ca-certificates gnupg lsb-release
```

---

## 2. Docker Engine & Docker Compose Installation

Install official Docker repository and runtime:

```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Docker Compose plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow current non-root user to run Docker commands
sudo usermod -aG docker $USER
newgrp docker

# Enable and verify Docker service status
sudo systemctl enable docker
sudo systemctl start docker
docker --version
docker compose version
```

---

## 3. Host Certbot & Nginx Tools Setup (Optional Native Utility Setup)

Install `certbot` for managing SSL certificates on the host machine:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## 4. Repository Setup & Environment Configuration

Create target deployment directory and clone repository:

```bash
sudo mkdir -p /opt/healthcare-voice-agent
sudo chown -R $USER:$USER /opt/healthcare-voice-agent
cd /opt/healthcare-voice-agent

# Clone the repository
git clone https://github.com/internexus/healthcare-voice-agent.git .

# Create and configure production environment variables
cp .env.example .env
nano .env
```

Ensure `.env` contains secure production parameters:

```env
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_USER=voiceagent
POSTGRES_PASSWORD=SuperSecureProductionPassword2026!
POSTGRES_DB=voiceagentdb
DATABASE_URL=postgresql://voiceagent:SuperSecureProductionPassword2026!@db:5432/voiceagentdb

SECRET_KEY=prod_super_secret_jwt_key_8493028491028349
ALLOWED_ORIGINS=["https://api.internexus.tech","https://grafana.internexus.tech","https://prometheus.internexus.tech"]
VAPI_WEBHOOK_SECRET=whsec_prod_9874563210_health_voice
LOG_LEVEL=INFO
```

---

## 5. Start Container Stack

Build and spin up containerized services in detached mode:

```bash
docker compose up -d --build
```

Verify running container status:

```bash
docker compose ps
```

---

## 6. Configure Nginx Reverse Proxy & Site Definitions

The project provides modular Nginx site configurations in `./nginx/conf.d/`. Ensure directory volume mounts are mapped correctly in `docker-compose.yml`:

```bash
# Verify config structure
ls -la ./nginx/
ls -la ./nginx/conf.d/
```

Test Nginx configuration syntax inside container:

```bash
docker compose exec nginx nginx -t
```

---

## 7. Generate Let's Encrypt SSL Certificates

Run Certbot via Docker or Native Certbot using HTTP-01 webroot challenge for all three domains:

```bash
# Ensure certbot volume directory exists
mkdir -p certbot_www nginx/certs

# Execute Certbot issuance
docker run -it --rm \
  -v $(pwd)/nginx/certs:/etc/letsencrypt \
  -v $(pwd)/certbot_www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d api.internexus.tech \
  -d grafana.internexus.tech \
  -d prometheus.internexus.tech \
  --email admin@internexus.tech \
  --agree-tos --no-eff-email
```

Enable the HTTPS server blocks inside `nginx/conf.d/api.conf`, `nginx/conf.d/grafana.conf`, and `nginx/conf.d/prometheus.conf`, then reload Nginx:

```bash
docker compose exec nginx nginx -s reload
```

---

## 8. UFW Firewall Configuration

Safeguard the Ubuntu server by enabling UFW firewall and restricting port access:

```bash
# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH, HTTP, and HTTPS
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Enable firewall
sudo ufw --force enable
sudo ufw status verbose
```

---

## 9. Verification & Post-Deployment Health Check

Test all production endpoints from host terminal or external browser:

```bash
# 1. API Health check
curl -i https://api.internexus.tech/health

# 2. Interactive Swagger Documentation
curl -I https://api.internexus.tech/docs

# 3. Grafana Dashboard
curl -I https://grafana.internexus.tech

# 4. Prometheus UI
curl -I https://prometheus.internexus.tech
```

---

## 10. Troubleshooting Guide

### Issue A: Port 80/443 Already in Use
```bash
# Find conflicting process listening on port 80 or 443
sudo lsof -i :80
sudo lsof -i :443
# Kill conflicting process if necessary
sudo systemctl stop apache2 || true
```

### Issue B: Database Connection Errors
```bash
# View PostgreSQL container logs
docker compose logs -f db
# Check database container health status
docker inspect --format='{{json .State.Health}}' healthcare_voice_db
```

### Issue C: Nginx Reverse Proxy 502 Bad Gateway
```bash
# Inspect Nginx error log
docker compose logs -f nginx
# Verify internal service responsiveness
docker compose exec nginx curl -i http://backend:8000/health
```

---

## 11. System Maintenance & Routine Operations Guide

### A. Automatic Certificate Renewal (Crontab)
Add a crontab task on host server (`crontab -e`):
```bash
0 3 1 * * docker run --rm -v /opt/healthcare-voice-agent/nginx/certs:/etc/letsencrypt -v /opt/healthcare-voice-agent/certbot_www:/var/www/certbot certbot/certbot renew && docker compose exec -T nginx nginx -s reload
```

### B. Viewing Real-Time Logs
```bash
# All containers
docker compose logs -f --tail=100

# Specific backend service
docker compose logs -f backend
```

### C. Database Backup & Restore
```bash
# Backup database to SQL dump
docker compose exec -T db pg_dump -U voiceagent voiceagentdb > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database from SQL dump
cat backup.sql | docker compose exec -T db psql -U voiceagent -d voiceagentdb
```

### D. System Cleanup & Resource Reclamation
```bash
# Prune unused Docker images, containers, and volumes
docker system prune -af --volumes
```
