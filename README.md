# Healthcare Voice Agent Backend

Production-ready Healthcare Voice Agent backend built with **FastAPI**, **Vapi AI Voice Platform**, **PostgreSQL**, **Docker**, **Nginx**, and **Prometheus/Grafana monitoring**.

## Architecture Highlights

- **Backend Framework**: Python 3.12 + FastAPI (Async worker)
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 Async Engine & Alembic migrations
- **Voice Platform**: Vapi Webhooks with HMAC-SHA256 signature security
- **Containerization**: Multi-stage Docker build & Docker Compose
- **Observability**: Prometheus metrics exporter & Grafana monitoring dashboard
- **Security**: Pydantic Settings, CORS restriction, JSON structured logging with trace propagation

## Directory Structure

```text
healthcare-voice-agent/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── src/
    └── app/
        ├── api/
        │   ├── v1/
        │   │   ├── endpoints/
        │   │   │   └── health.py
        │   │   └── router.py
        │   └── deps.py
        ├── core/
        │   ├── config.py
        │   ├── settings.py
        │   ├── database.py
        │   ├── logging.py
        │   └── middleware.py
        ├── dependencies.py
        └── main.py
```

## Local Setup & Quick Start

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Start full containerized stack using Docker Compose:
   ```bash
   docker compose up -d
   ```

3. Access Application Services:
   - **FastAPI Documentation**: `http://localhost:8000/docs` or `http://api.internexus.tech/docs`
   - **Vapi Webhook Endpoint**: `POST http://localhost:8000/webhook/vapi`
   - **Prometheus UI**: `http://localhost:9090` or `http://prometheus.internexus.tech`
   - **Grafana Dashboard**: `http://localhost:3001` or `http://grafana.internexus.tech` *(Default Login: admin / admin)*
   - **FastAPI Metrics Endpoint**: `http://localhost:8000/metrics`
   - **Node Exporter Host Metrics**: `http://localhost:9100/metrics`
   - **cAdvisor Container Metrics**: `http://localhost:8080/metrics`

---

## Observability & Monitoring Setup

The infrastructure includes an enterprise observability stack out-of-the-box:

- **Prometheus Exporter**: Exposes real-time HTTP latency, request throughput (RPS), error counts, and process memory via `prometheus_fastapi_instrumentator`.
- **Node Exporter**: Collects host system hardware metrics (CPU utilization, RAM consumption, disk I/O, network bandwidth).
- **cAdvisor**: Scrapes container-level CPU, memory usage, and lifecycle statistics across all running Docker containers.
- **Prometheus Server**: Automatically scrapes backend (`backend:8000`), Node Exporter (`node-exporter:9100`), and cAdvisor (`cadvisor:8080`) at 15-second intervals.
- **Grafana Provisioning**: Automatically pre-loads the Prometheus datasource and provisions the `Healthcare Voice Agent Infrastructure Dashboard` (`/grafana/provisioning/dashboards/healthcare_dashboard.json`).

---

