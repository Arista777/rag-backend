from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


settings = get_settings()
configure_logging(settings.app_debug)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
allow_credentials = "*" not in origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
