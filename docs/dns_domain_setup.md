# Comprehensive DNS, Domain & Networking Setup Guide

This guide provides complete instructions for configuring DNS domain records, SSL certificate issuance, reverse proxy routing, and webhook endpoints for **`internexus.tech`**.

---

## 1. Domain Overview & A Records Architecture

To expose the Healthcare Voice Agent backend, monitoring stack, and dashboard publicly, configure the following **A Records** in your DNS provider (e.g. Cloudflare, Namecheap, Route 53, GoDaddy):

| Subdomain / Host | Record Type | Target IPv4 Address | Description / Destination Service |
| :--- | :--- | :--- | :--- |
| `api.internexus.tech` | **A** | `YOUR_SERVER_PUBLIC_IP` | FastAPI Backend & Vapi Webhook Proxy |
| `grafana.internexus.tech` | **A** | `YOUR_SERVER_PUBLIC_IP` | Grafana Monitoring & Analytics Dashboard |
| `prometheus.internexus.tech` | **A** | `YOUR_SERVER_PUBLIC_IP` | Prometheus Time-Series Metrics UI |
| `@` / `internexus.tech` | **A** | `YOUR_SERVER_PUBLIC_IP` | Root Domain Pointer (Optional) |

> **Note**: Replace `YOUR_SERVER_PUBLIC_IP` with the static public IPv4 address of your production cloud instance (e.g. AWS EC2, DigitalOcean Droplet, GCP Compute Engine, Hetzner).

---

## 2. DNS Propagation & TTL Mechanics

- **TTL (Time to Live)**: Set your DNS record TTL to **300 seconds (5 minutes)** or **Automatic**.
- **Global Propagation Duration**: DNS record updates usually propagate worldwide within 2 to 15 minutes, depending on recursive DNS caching servers (Google `8.8.8.8`, Cloudflare `1.1.1.1`).
- **Propagation Checking Tools**:
  - Web UI: [https://dnschecker.org/#A/api.internexus.tech](https://dnschecker.org/#A/api.internexus.tech)
  - Global Resolver Ping: Test query resolution across multiple continents.

---

## 3. DNS Record Verification Commands

Run these terminal commands on your local machine or server to verify DNS resolution before issuing SSL certificates:

### A. Using `dig`:
```bash
# Verify API subdomain
dig +short api.internexus.tech

# Verify Grafana subdomain
dig +short grafana.internexus.tech

# Verify Prometheus subdomain
dig +short prometheus.internexus.tech
```

### B. Using `nslookup`:
```bash
nslookup api.internexus.tech 8.8.8.8
```

### C. Testing HTTP Reachability:
```bash
curl -I http://api.internexus.tech/health
```
*(Should return `HTTP/1.1 200 OK` routed through Nginx).*

---

## 4. Let's Encrypt SSL/TLS Certificate Issuance

Once DNS records point to your server IP, obtain free, automated 90-day TLS/SSL certificates using Let's Encrypt's **ACME HTTP-01 Webroot challenge**.

### How HTTP-01 Validation Works:
1. Certbot writes a token file to `/var/www/certbot/.well-known/acme-challenge/<TOKEN>`.
2. Let's Encrypt validation servers send an HTTP query to `http://api.internexus.tech/.well-known/acme-challenge/<TOKEN>`.
3. Nginx serves the token from the shared `certbot_www` Docker volume.
4. Upon successful match, Let's Encrypt issues the signed certificate files (`fullchain.pem` & `privkey.pem`).

### Step-by-Step Certificate Generation Command:
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

---

## 5. Nginx Reverse Proxy Routing Mechanics

Nginx acts as the single edge entry point listening on public ports `80` (HTTP) and `443` (HTTPS). It reads incoming `Host` request headers and proxies traffic to internal isolated container services on the `app-network`:

```
                                  ┌───> backend:8000 (FastAPI API & Webhooks)
                                  │
[Client Request] ──> Nginx (80/443) ──> grafana:3000 (Grafana Dashboard)
                                  │
                                  └───> prometheus:9090 (Prometheus UI)
```

- **`api.internexus.tech`** -> proxied to `http://backend:8000`
- **`grafana.internexus.tech`** -> proxied to `http://grafana:3000`
- **`prometheus.internexus.tech`** -> proxied to `http://prometheus:9090`

---

## 6. Vapi Voice Webhook Endpoint Integration

In the **Vapi AI Dashboard** ([https://dashboard.vapi.ai](https://dashboard.vapi.ai)), configure your Voice Assistant Server URL:

- **Server URL**: `https://api.internexus.tech/webhook/vapi`
- **Secret Header**: `x-vapi-secret`
- **Secret Value**: Must match your `VAPI_WEBHOOK_SECRET` environment variable (e.g., `whsec_prod_9874563210_health_voice`).

---

## 7. Final Production Endpoint URLs

| Service / Interface | Public URL | Protocol / Port |
| :--- | :--- | :--- |
| **FastAPI Base API** | `https://api.internexus.tech` | HTTPS (443) |
| **Interactive API Documentation** | `https://api.internexus.tech/docs` | HTTPS (443) |
| **Vapi Webhook Endpoint** | `https://api.internexus.tech/webhook/vapi` | HTTPS (443) |
| **System Healthcheck Endpoint** | `https://api.internexus.tech/health` | HTTPS (443) |
| **Grafana Monitoring Dashboard** | `https://grafana.internexus.tech` | HTTPS (443) |
| **Prometheus Metrics UI** | `https://prometheus.internexus.tech` | HTTPS (443) |
