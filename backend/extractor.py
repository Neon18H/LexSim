"""Utilities to extract structured JSON blocks from model responses."""
from __future__ import annotations

import json
import logging
import re
from typing import Callable, List, Optional, Tuple

from pydantic import ValidationError

from .schemas import SimulationJSON

LOGGER = logging.getLogger(__name__)
JSON_BLOCK_PATTERN = re.compile(
    r"```json\s*(?P<json>[\s\S]*?)\s*```",
    re.IGNORECASE,
)
TRAILING_COMMA_PATTERN = re.compile(r",(?=\s*[}\]])")


def _try_parse_json(
    json_text: str, transformers: Optional[List[Callable[[str], str]]] = None
) -> Tuple[Optional[SimulationJSON], Optional[Exception]]:
    """Attempt to parse the JSON text using optional sanitizers."""

    transformers = transformers or [lambda value: value]
    last_error: Optional[Exception] = None
    for transform in transformers:
        candidate = transform(json_text)
        try:
            parsed = json.loads(candidate.strip())
            return SimulationJSON.parse_obj(parsed), None
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            continue
    return None, last_error


def _strip_json_comments(json_text: str) -> str:
    """Strip C/C++ style comments that appear outside of strings."""

    result: List[str] = []
    length = len(json_text)
    index = 0
    in_string = False
    escape = False

    while index < length:
        char = json_text[index]

        if escape:
            result.append(char)
            escape = False
            index += 1
            continue

        if char == "\\":
            escape = True
            result.append(char)
            index += 1
            continue

        if char == '"':
            in_string = not in_string
            result.append(char)
            index += 1
            continue

        if not in_string and char == "/" and index + 1 < length:
            next_char = json_text[index + 1]
            if next_char == "/":
                index += 2
                while index < length and json_text[index] not in {"\n", "\r"}:
                    index += 1
                continue
            if next_char == "*":
                index += 2
                while index + 1 < length:
                    if json_text[index] == "*" and json_text[index + 1] == "/":
                        index += 2
                        break
                    index += 1
                continue

        result.append(char)
        index += 1

    return "".join(result)


def _sanitize_json(json_text: str) -> str:
    """Remove common issues introduced by LLMs in JSON payloads."""

    without_comments = _strip_json_comments(json_text)
    sanitized = re.sub(TRAILING_COMMA_PATTERN, "", without_comments)
    return sanitized


def _find_matching_brace(raw_text: str, start: int) -> Optional[int]:
    """Return the index of the matching closing brace for the given start."""

    depth = 0
    in_string = False
    escape = False

    for idx in range(start, len(raw_text)):
        char = raw_text[idx]

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return idx

    return None


def _find_json_block(raw_text: str) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
    """Locate the JSON payload and return both its text and span."""

    match = JSON_BLOCK_PATTERN.search(raw_text)
    if match:
        json_content = match.group("json")
        return json_content, match.span()

    start = raw_text.find("{")
    while start != -1:
        end = _find_matching_brace(raw_text, start)
        if end is None:
            break
        candidate = raw_text[start : end + 1]
        try:
            json.loads(candidate)
            return candidate, (start, end + 1)
        except json.JSONDecodeError:
            start = raw_text.find("{", start + 1)
            continue

    return None, None


def extract_simulation_payload(raw_text: str) -> Tuple[str, Optional[SimulationJSON], List[str]]:
    """Split the model response into markdown and structured JSON."""

    warnings: List[str] = []
    json_block, span = _find_json_block(raw_text)
    simulation_data: Optional[SimulationJSON] = None

    if json_block:
        transformers = [lambda value: value, _sanitize_json]
        simulation_data, last_error = _try_parse_json(json_block, transformers)

        if simulation_data is None and last_error is not None:
            warnings.append(
                "No se pudo validar el bloque JSON generado. Se entrega solo el Markdown."
            )
            LOGGER.warning("JSON extraction failed after sanitization: %s", last_error)
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
        if simulation_data is None:
            warnings.append(
                "El modelo no devolvió contenido en Markdown ni proporcionó un JSON estructurado válido."
            )
        else:
            warnings.append(
                "El modelo no devolvió contenido en Markdown. Se entrega solo el JSON estructurado disponible."
            )

    return cleaned_markdown, simulation_data, warnings


__all__ = ["extract_simulation_payload"]
