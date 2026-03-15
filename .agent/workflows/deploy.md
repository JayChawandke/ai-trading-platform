---
description: Deploy the AI Trading Platform using Docker Compose
---

This workflow helps you deploy the application in a production-ready containerized environment.

1. Ensure you have Docker and Docker Compose installed.
2. Create a `.env` file from `.env.example` if it doesn't exist.
   ```bash
   cp .env.example .env
   ```
3. Update the `.env` file with your production values (Database password, URLs, etc.).
// turbo
4. Run the deployment command:
   ```bash
   docker-compose up --build -d
   ```
5. Verify the services are running:
   ```bash
   docker-compose ps
   ```
6. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - ML Service: http://localhost:8001
