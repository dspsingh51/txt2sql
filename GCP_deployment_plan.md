# GCP Deployment Plan for txt2sql

This deployment plan outlines how to transition the `txt2sql` multi-agent project from a local SQLite setup to a robust, cloud-native architecture on Google Cloud Platform (GCP). It utilizes **Cloud SQL for PostgreSQL** as the database and exposes the application to end users via a **Public IP Address**.

---

## 1. Optimal Cloud Architecture

```mermaid
graph TD
    User[End Users] -->|HTTP/HTTPS via Public IP| GlobalLB[GCP Global HTTP(S) Load Balancer]
    
    subgraph GCP_Environment [GCP Environment]
        GlobalLB -->|Routes Traffic| Frontend[Cloud Run: Streamlit Frontend]
        
        Frontend -->|Internal API Calls| Backend[Cloud Run: FastAPI Backend]
        
        subgraph Managed_Services [Managed Services]
            Backend -->|VPC Peering/Private IP| CloudSQL[(Cloud SQL: PostgreSQL)]
        end
        
        subgraph External_LLM [External LLM]
            Backend -->|API Keys| Gemini[Google Gemini API]
        end
    end
```

### Components:
- **Cloud SQL for PostgreSQL**: Replaces the local SQLite database. It holds the schema, metadata, and business data being queried.
- **Cloud Run (Backend & Frontend)**: Serverless compute that automatically scales. We deploy the FastAPI backend and Streamlit frontend as separate microservices.
- **Global External HTTP(S) Load Balancer**: Provides a single static IPv4 address to expose the Streamlit frontend to the public internet securely.

---

## 2. Preparing the Application for PostgreSQL

The `txt2sql` project is already designed to support PostgreSQL via its SQLAlchemy integration. To switch from SQLite to PostgreSQL in production, you must set the appropriate environment variables.

Your backend service will need the following environment variables set:
```ini
DATABASE_DIALECT=postgres
POSTGRES_HOST=10.x.x.x  # The private IP of your Cloud SQL instance
POSTGRES_PORT=5432
POSTGRES_USER=txt2sql_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=txt2sql_prod
GEMINI_API_KEY=your_gemini_api_key
```

---

## 3. Step-by-Step Deployment Guide

### Phase 1: Provision the PostgreSQL Database
1. Go to the GCP Console and navigate to **SQL**.
2. Create a new **PostgreSQL** instance.
3. Under **Connections**, ensure **Private IP** is enabled and configured to your default VPC network. (Disable Public IP for security).
4. Create a database named `txt2sql_prod`.
5. Create a user named `txt2sql_user` with a secure password.
6. Run the database seed scripts (`sql_engine/seed.py`) against this new Cloud SQL instance to populate the tables and mock data.

### Phase 2: Build and Push Docker Images
Google Artifact Registry (GAR) is used to store your container images.

```bash
# Set variables
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Build Backend Image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/repo/txt2sql-backend -f Dockerfile .
# (Note: You may need separate Dockerfiles for frontend/backend, or use the single Dockerfile with different entrypoints)

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/repo/txt2sql-backend
```

### Phase 3: Deploy to Cloud Run
Deploy both services into the same region and connect them to the VPC.

**Deploy the Backend:**
Ensure you attach a Serverless VPC Access connector so Cloud Run can communicate with the Cloud SQL Private IP.
```bash
gcloud run deploy txt2sql-backend \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/repo/txt2sql-backend \
  --region $REGION \
  --vpc-egress all-traffic \
  --set-env-vars="DATABASE_DIALECT=postgres,POSTGRES_HOST=<SQL_PRIVATE_IP>,POSTGRES_USER=txt2sql_user,POSTGRES_PASSWORD=<PASSWORD>,POSTGRES_DB=txt2sql_prod,GEMINI_API_KEY=<API_KEY>"
```

**Deploy the Frontend (Streamlit):**
Point the frontend to the newly generated Backend URL.
```bash
gcloud run deploy txt2sql-frontend \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/repo/txt2sql-frontend \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="BACKEND_URL=https://txt2sql-backend-xyz.a.run.app"
```

### Phase 4: Expose via a Static Public IP
By default, Cloud Run gives you a `run.app` URL. To assign a strict static Public IP address:
1. Navigate to **VPC Network > IP addresses** and reserve a static external IPv4 address.
2. Navigate to **Network Services > Load balancing**.
3. Create an **HTTP(S) Load Balancer**.
4. Set the **Backend configuration** to route to a Serverless Network Endpoint Group (NEG) attached to your `txt2sql-frontend` Cloud Run service.
5. Set the **Frontend configuration** to use the static IP you reserved.
6. Once provisioned, users can navigate to `http://<YOUR_STATIC_IP>` in their browser to access the natural language querying interface.

---

## 4. Security Considerations for Production

- **Read-Only Database User**: For maximum security against SQL injection, the `txt2sql_user` in PostgreSQL should be strictly limited to `SELECT` permissions on the operational tables.
- **API Key Management**: Store the `GEMINI_API_KEY` and `POSTGRES_PASSWORD` in **Google Secret Manager** and inject them into Cloud Run, rather than passing them as plain text environment variables.
