
# AI Trading Platform (Full Scaffold)

Production-style architecture:

- FastAPI backend
- PostgreSQL + SQLAlchemy
- Redis for caching/pubsub
- ML microservice (PyTorch-ready)
- React frontend dashboard
- Dockerized microservices
- WebSocket market streaming
- Strategy + backtesting modules

Run:

docker-compose up --build

Services:
- Backend API: http://localhost:8000
- ML Service: http://localhost:8001
- Frontend: http://localhost:3000
