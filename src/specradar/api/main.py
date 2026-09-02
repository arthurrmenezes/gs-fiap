"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from specradar.api.routes import router
from specradar.config import REPO_ROOT, get_settings
from specradar.logging import configure_logging, get_logger
from specradar.taxonomy.loader import get_taxonomy

log = get_logger("app")

# Dev origins for the Vite frontend. Production serves the built SPA same-origin.
_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
]

_FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    # Fail fast if the taxonomy is broken — it is the source of truth.
    tax = get_taxonomy()
    log.info("startup", env=settings.env, attributes=len(tax.all_attributes()))
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SpecRadar",
        version="0.1.0",
        summary="Automotive competitive intelligence — standardized, auditable spec sheets.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_DEV_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # API under /api so the SPA can own the root path in production.
    app.include_router(router, prefix="/api")

    _mount_frontend(app)
    return app


def _mount_frontend(app: FastAPI) -> None:
    """Serve the built SPA at the root if it has been built (`frontend/dist`)."""
    if not _FRONTEND_DIST.is_dir():
        return
    app.mount("/", StaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")
    log.info("frontend_mounted", dist=str(_FRONTEND_DIST))


app = create_app()
