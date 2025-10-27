"""Utility helpers to prepare requests for the simulation service."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from pydantic import BaseModel


@dataclass(slots=True)
class SimulationInput:
    """Internal representation of the simulation payload."""

    prompt: str
    options: Dict[str, Any] = field(default_factory=dict)


def _coerce_parameters(parameters: Optional[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model into a serialisable dictionary."""

    if parameters is None:
        return {}
    data = parameters.dict(exclude_none=True)
    return {key: value for key, value in data.items() if value is not None}


def build_simulation_input(prompt: str, parameters: Optional[BaseModel]) -> SimulationInput:
    """Create an internal simulation input structure."""

    return SimulationInput(prompt=prompt.strip(), options=_coerce_parameters(parameters))
