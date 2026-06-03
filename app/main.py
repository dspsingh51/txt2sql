from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from configs.logging import configure_logging
from configs.settings import get_settings

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Enterprise-grade natural language analytics and governed text-to-SQL platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "environment": settings.app_env}
