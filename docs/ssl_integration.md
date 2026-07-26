# SSL / TLS Certificate Integration & HTTPS Setup Guide

This document explains how to set up HTTPS/TLS certificates for `api.internexus.tech`, `grafana.internexus.tech`, and `prometheus.internexus.tech` using **Let's Encrypt** and **Certbot** with Nginx.

---

## 1. Overview & Architecture

Nginx is configured as the TLS termination reverse proxy for all incoming public web traffic on ports `80` (HTTP) and `443` (HTTPS):

- **Port 80 (HTTP)**: Serves ACME Webroot challenge requests (`/.well-known/acme-challenge/`) for automated Let's Encrypt validation and redirects standard traffic to HTTPS.
- **Port 443 (HTTPS)**: Encrypts incoming traffic using modern TLS 1.2 / TLS 1.3 ciphers and proxies requests internally to backend containers.

---

## 2. Option A: Let's Encrypt (Production Setup)

### Step 1: Ensure DNS A Records
Verify that your domain DNS records point to your server's public IP:
- `api.internexus.tech` -> `YOUR_SERVER_PUBLIC_IP`
- `grafana.internexus.tech` -> `YOUR_SERVER_PUBLIC_IP`
- `prometheus.internexus.tech` -> `YOUR_SERVER_PUBLIC_IP`

### Step 2: Request Certificates via Certbot Docker Container
Run the following Certbot command on your server host to obtain production certificates using webroot mode:

```bash
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

### Step 3: Enable HTTPS Server Blocks in Nginx Configs
Uncomment the HTTPS `server { listen 443 ssl http2; ... }` blocks in:
- `nginx/conf.d/api.conf`
- `nginx/conf.d/grafana.conf`
- `nginx/conf.d/prometheus.conf`

Ensure the certificate file paths match:
```nginx
ssl_certificate /etc/nginx/certs/live/api.internexus.tech/fullchain.pem;
ssl_certificate_key /etc/nginx/certs/live/api.internexus.tech/privkey.pem;
```

### Step 4: Reload Nginx Configuration
```bash
docker compose exec nginx nginx -s reload
```

---

## 3. Automated Certificate Renewal

Let's Encrypt certificates are valid for 90 days. Set up a crontab entry on the host to auto-renew every month:

```bash
0 3 1 * * docker run --rm -v $(pwd)/nginx/certs:/etc/letsencrypt -v $(pwd)/certbot_www:/var/www/certbot certbot/certbot renew && docker compose exec nginx nginx -s reload
```

---

## 4. Option B: Self-Signed Certificates (Local Development / Staging)

For local development or testing HTTPS without public DNS:

```bash
mkdir -p nginx/certs/live/api.internexus.tech

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/live/api.internexus.tech/privkey.pem \
  -out nginx/certs/live/api.internexus.tech/fullchain.pem \
  -subj "/CN=api.internexus.tech/O=InterNexus"
```

Then reload Nginx:
```bash
docker compose exec nginx nginx -t
docker compose exec nginx nginx -s reload
```

---

## 5. Security & Cipher Best Practices Included

The Nginx setup automatically includes:
- **Protocols**: TLSv1.2, TLSv1.3
- **Cipher Suite**: Strong Forward Secrecy (ECDHE-ECDSA/RSA-AES128/256-GCM)
- **HSTS Header**: `Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"`
- **Rate Limiting**: Defends against DDoS and payload spam
- **Gzip Compression**: Compresses JSON responses for optimized throughput
