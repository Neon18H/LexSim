"""FastAPI application for the LexSim backend."""
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import extractor, service_llm
from .settings import get_settings


class SimulationParameters(BaseModel):
    """Optional parameters that control the simulation process."""

    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Controls the randomness of the simulation output.",
    )
    max_steps: int | None = Field(
        default=None,
        ge=1,
        description="Maximum number of narrative steps to generate.",
    )


class SimulationRequest(BaseModel):
    """Payload submitted by the frontend to start a simulation."""

    prompt: str = Field(..., description="Scenario description used for the simulation.")
    parameters: SimulationParameters | None = Field(
        default=None, description="Optional configuration values for the simulation."
    )


class SimulationResponse(BaseModel):
    """Standardised response returned from the simulation service."""

    prompt: str
    steps: list[str]
    summary: str
    metadata: Dict[str, Any]


settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.version)


@app.get("/health")
def health() -> Dict[str, str]:
    """Simple health check endpoint used for monitoring and testing."""

    return {"status": "ok", "service": settings.app_name}


@app.post("/api/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest) -> SimulationResponse:
    """Run a lightweight simulation based on the provided prompt."""

    if not request.prompt.strip():
        raise HTTPException(status_code=422, detail="The prompt must not be empty.")

    simulation_input = extractor.build_simulation_input(request.prompt, request.parameters)
    result = service_llm.run_simulation(simulation_input)
    return SimulationResponse(**result)


__all__ = ["app"]
