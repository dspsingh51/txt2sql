# Deployment

Use Docker Compose for local deployment:

```bash
docker compose up --build
```

For cloud deployment, adapt the container images to ECS, EKS, Kubernetes, or any platform that supports FastAPI, Streamlit, Redis, and a read-only analytics database.
