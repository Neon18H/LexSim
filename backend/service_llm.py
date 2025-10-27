"""Mock LLM service used by the API to generate deterministic results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .extractor import SimulationInput
from .settings import get_settings


@dataclass(slots=True)
class SimulationResult:
    """Human readable result returned to the API."""

    prompt: str
    steps: List[str]
    summary: str
    metadata: Dict[str, float | int]


def _generate_steps(prompt: str, max_steps: int | None) -> List[str]:
    """Create a sequence of narrative steps based on the prompt."""

    base_words: Iterable[str] = (word.strip(",.;:!") for word in prompt.split())
    words = [word for word in base_words if word]
    if not words:
        return ["No meaningful content supplied."]

    limit = max_steps or min(len(words), 5)
    limit = max(1, limit)
    return [f"Step {index + 1}: {word.capitalize()}" for index, word in enumerate(words[:limit])]


def run_simulation(simulation_input: SimulationInput) -> Dict[str, object]:
    """Generate a deterministic simulation from the request payload."""

    settings = get_settings()
    options = simulation_input.options
    max_steps = options.get("max_steps") if isinstance(options, dict) else None

    steps = _generate_steps(simulation_input.prompt, max_steps)
    summary = (
        f"Simulation using model {settings.llm_model_name} produced {len(steps)} step(s)."
    )
    metadata: Dict[str, float | int] = {
        "token_count": len(simulation_input.prompt.split()),
        "step_count": len(steps),
    }
    if temperature := options.get("temperature") if isinstance(options, dict) else None:
        metadata["temperature"] = temperature

    result = SimulationResult(
        prompt=simulation_input.prompt,
        steps=steps,
        summary=summary,
        metadata=metadata,
    )
    return {
        "prompt": result.prompt,
        "steps": result.steps,
        "summary": result.summary,
        "metadata": result.metadata,
    }
