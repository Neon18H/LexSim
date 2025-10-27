"""Utilities to extract structured JSON blocks from model responses."""
from __future__ import annotations

import json
import logging
import re
from typing import List, Optional, Tuple

from pydantic import ValidationError

from .schemas import SimulationJSON

LOGGER = logging.getLogger(__name__)
JSON_BLOCK_PATTERN = re.compile(
    r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE
)


def _find_json_block(raw_text: str) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
    """Locate the JSON payload and return both its text and span."""

    match = JSON_BLOCK_PATTERN.search(raw_text)
    if match:
        return match.group(1), match.span()

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw_text[start : end + 1], (start, end + 1)

    return None, None


def extract_simulation_payload(raw_text: str) -> Tuple[str, Optional[SimulationJSON], List[str]]:
    """Split the model response into markdown and structured JSON."""

    warnings: List[str] = []
    json_block, span = _find_json_block(raw_text)
    simulation_data: Optional[SimulationJSON] = None

    if json_block:
        try:
            parsed = json.loads(json_block)
            simulation_data = SimulationJSON.parse_obj(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            warnings.append(
                "No se pudo validar el bloque JSON generado. Se entrega solo el Markdown."
            )
            LOGGER.warning("JSON extraction failed: %s", exc)
    else:
        warnings.append(
            "No se detectó un bloque JSON válido en la respuesta del modelo."
        )

    if span:
        markdown_part = raw_text[: span[0]] + raw_text[span[1] :]
    else:
        markdown_part = raw_text

    cleaned_markdown = markdown_part.strip()

    if not cleaned_markdown:
        warnings.append(
            "El modelo no devolvió contenido en Markdown. Se entrega solo el JSON estructurado disponible."
        )

    return cleaned_markdown, simulation_data, warnings


__all__ = ["extract_simulation_payload"]
