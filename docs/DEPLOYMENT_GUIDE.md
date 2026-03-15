# Deployment Guide: AI Trading Platform

This guide covers how to deploy the application for end users in a production-like environment.

## Prerequisites
- **Server**: A Linux/Windows server with at least 4GB RAM (8GB recommended for ML services).
- **Runtime**: Docker and Docker Compose installed.
- **Node.js**: v18+ (for local builds if not using Docker builder).

## 1. Environment Configuration

Create a `.env` file in the root directory based on `.env.example`.

```env
# Database
POSTGRES_USER=trading
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=trading

# Security
SECRET_KEY=generate_a_long_random_string

# URLs (Important for Frontend-Backend communication)
REACT_APP_BACKEND_URL=http://your-server-ip:8000
REACT_APP_ML_SERVICE_URL=http://your-server-ip:8001
```

## 2. Docker Deployment

Deploy all services (Backend, Frontend, ML, PostgreSQL, Redis) using Docker Compose:

```bash
docker-compose up --build -d
```

Validating the deployment:
- **Backend API**: `http://your-server-ip:8000/health`
- **Frontend UI**: `http://your-server-ip:3000`
- **ML Service**: `http://your-server-ip:8001/health` (verify manually if health endpoint exists)

## 3. Production Hardening

### Reverse Proxy (Nginx)
It is recommended to use Nginx as a reverse proxy to handle SSL (HTTPS) and route traffic to the services.

### Database Backups
Ensure you have a backup strategy for the `pgdata` volume.

### CORS Setup
Before going live, update `backend/app/main.py` to restrict `allow_origins`:

```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"], # restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 4. Monitoring
- Use `docker logs -f backend` to monitor real-time errors.
- Monitor Redis memory usage for large scales.
