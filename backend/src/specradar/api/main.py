"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from specradar.api.routes import router
from specradar.config import get_settings
from specradar.logging import configure_logging, get_logger
from specradar.taxonomy.loader import get_taxonomy

log = get_logger("app")


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
        version="1.0.0",
        summary="Backend do app mobile SpecRadar — fichas técnicas padronizadas.",
        lifespan=lifespan,
    )
    # The mobile app calls the API directly; CORS only matters for Expo Web.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    return app


app = create_app()
