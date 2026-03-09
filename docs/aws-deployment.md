# AWS Deployment Guide

## 1. Target Architecture
- Frontend container on ECS Fargate behind Application Load Balancer.
- Backend container on ECS Fargate behind the same ALB (path-based routing `/api/*`).
- Persistent storage:
  - Amazon EFS mounted to backend container for `data/` (SQLite + FAISS files), or
  - Replace SQLite with Amazon RDS and vector store with managed service later.
- Secrets in AWS Secrets Manager (OpenAI key).

## 2. Build and Push Images
1. Create ECR repositories (`assistant-frontend`, `assistant-backend`).
2. Build images locally:
   - `docker build -f docker/backend.Dockerfile -t assistant-backend:latest .`
   - `docker build -f docker/frontend.Dockerfile -t assistant-frontend:latest .`
3. Tag and push to ECR.

## 3. Configure ECS
1. Create ECS cluster (Fargate).
2. Create task definitions:
   - Backend task port `8000`.
   - Frontend task port `3000`.
3. Add env vars to backend task:
   - `OPENAI_API_KEY`
   - `OPENAI_CHAT_MODEL`
   - `OPENAI_EMBEDDING_MODEL`
   - `ALLOWED_ORIGINS`
4. Mount persistent volume for `/app/data`.

## 4. Load Balancer Routing
- `/api/*` -> backend target group (port 8000)
- `/*` -> frontend target group (port 3000)

## 5. Production Notes
- Enable HTTPS with ACM certificate on ALB.
- Use CloudWatch logs for both services.
- Set autoscaling policies based on CPU/memory.
- For high scale, move chat history to RDS and vector retrieval to a managed vector DB.
