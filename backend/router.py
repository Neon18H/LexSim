"""API router definitions for LexSim backend."""
from __future__ import annotations

import logging
import time
from collections import deque
from typing import Deque, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from .extractor import extract_simulation_payload
from .schemas import SimulateRequest, SimulateResponse
from .service_llm import SYSTEM_PROMPT, build_user_prompt, call_openrouter
from .settings import get_settings

LOGGER = logging.getLogger(__name__)
router = APIRouter()
_REQUEST_LOG: Dict[str, Deque[float]] = {}


def rate_limiter(request: Request) -> None:
    """Simple sliding-window rate limiter per client IP."""

    settings = get_settings()
    limit = settings.rate_limit_per_minute
    window_seconds = 60.0
    ip = request.client.host if request.client else "unknown"
    now = time.time()

    bucket = _REQUEST_LOG.setdefault(ip, deque())
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()

    if len(bucket) >= limit:
        LOGGER.warning("Rate limit exceeded for %s", ip)
        raise HTTPException(
            status_code=429,
            detail="Límite de peticiones excedido. Intente nuevamente más tarde.",
        )

    bucket.append(now)


@router.get("/health")
async def healthcheck() -> Dict[str, str]:
    """Health check endpoint."""

    return {"status": "ok"}


@router.post("/api/simulate", response_model=SimulateResponse)
async def simulate_endpoint(
    request_payload: SimulateRequest, _=Depends(rate_limiter)
) -> SimulateResponse:
    """Generate a simulation using the configured language model."""

    start = time.perf_counter()
    try:
        user_prompt = build_user_prompt(request_payload)
        raw_response = await call_openrouter(SYSTEM_PROMPT, user_prompt)
        markdown, json_data, warnings = extract_simulation_payload(raw_response)
        return SimulateResponse(
            markdown=markdown, simulation_json=json_data, warnings=warnings
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        LOGGER.exception("Simulation generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Error al generar la simulación. Intente nuevamente más tarde.",
        ) from exc
    finally:
        elapsed = time.perf_counter() - start
        LOGGER.info("Simulation processed in %.2fs", elapsed)


__all__ = ["router"]
