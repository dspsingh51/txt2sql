# AWS-Ready Deployment Notes

This repository is deployable locally with Docker Compose and can be adapted to AWS with managed services.

## Reference AWS Architecture

- Amazon ECS or EKS for FastAPI and Streamlit containers
- Application Load Balancer for HTTPS ingress
- Amazon ElastiCache for Redis memory
- Amazon RDS PostgreSQL read replica or Redshift Serverless for analytics execution
- AWS Secrets Manager for Gemini and database credentials
- Amazon CloudWatch for logs and metrics
- AWS WAF for perimeter protection
- IAM roles for service-to-service access

## Production Hardening

- Use private subnets for application containers and databases
- Enforce TLS everywhere
- Store secrets outside environment files
- Add identity-aware access through SSO or Cognito
- Restrict database credentials to read-only permissions
- Enable query timeouts and statement limits
- Export audit logs to immutable storage
- Add CI checks for SQL validator regression tests
