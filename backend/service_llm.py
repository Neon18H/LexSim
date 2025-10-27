"""Service layer to interact with OpenRouter LLMs."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

import httpx

from .schemas import SimulateRequest
from .settings import get_settings

LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres LexSim, un agente pedagógico experto en simulaciones de juicios para estudiantes de habla hispana. Tu misión es generar DOS salidas con base en el contexto proporcionado: (1) un informe en Markdown didáctico que incluya objetivos, narrativa y guion completo de la simulación; (2) un bloque JSON **válido** que siga exactamente el esquema proporcionado. Reglas estrictas:
- Nunca incluyas datos reales ni información sensible; todo debe ser ficticio.
- Si no se especifica la jurisdicción, asume un proceso penal acusatorio hispano genérico.
- Incluye objeciones frecuentes, consideraciones de cadena de custodia y hashes simulados para evidencia digital.
- Estructura la respuesta en el siguiente orden: primero el Markdown pedagógico, luego un bloque de código etiquetado como ```json ... ``` con el objeto JSON ajustado al esquema.
- Asegúrate de que el JSON sea auto-contenido, sin comentarios, sin texto adicional ni explicaciones externas.
- Respeta el tipo de materia, nivel y objetivo didáctico solicitados.

Esquema JSON obligatorio:
{
  "meta": {
    "titulo": "string",
    "jurisdiccion": "string",
    "materia": "string",
    "nivel": "basico|intermedio|avanzado",
    "objetivo_didactico": "string",
    "duracion_minutos": 90
  },
  "personajes": [
    {"nombre": "string","rol": "juez|fiscal|defensa|demandante|demandado|testigo|perito|policia|otro","bio": "string","objetivos": ["string"],"sesgos": ["string"]}
  ],
  "cronologia": [{"t": "YYYY-MM-DD HH:MM", "evento": "string"}],
  "planteamiento_juridico": {
    "tipo": "penal|civil|laboral|administrativo|otro",
    "cargos_o_pretensiones": ["string"],
    "estandar_probatorio": "string",
    "notas": "string"
  },
  "pruebas": {
    "documental": [{"id":"DOC-01","descripcion":"string","origen":"string","autenticidad_custodia":"string","posibles_objeciones":["string"]}],
    "testimonial": [{"id":"TES-01","testigo":"string","alcance":"string","riesgos_credibilidad":["string"],"contrapreguntas_sugeridas":["string"]}],
    "pericial":   [{"id":"PER-01","area":"string","metodo":"string","limites":"string","validez":"string"}],
    "digital_fisica": [{"id":"DIG-01","tipo":"digital|fisica","descripcion":"string","hash":"abc123...","metadatos":{"k":"v"},"cadena_custodia":"string"}]
  },
  "guion": {
    "instrucciones_iniciales_juez": "string",
    "apertura": {"parte_1": "string","parte_2": "string"},
    "interrogatorios": [{"tipo":"directo|contrainterrogatorio","a_quien":"string","preguntas":["string"]}],
    "objeciones_tipicas": [{"objecion":"leading","fundamento":"string"}],
    "cierre": {"parte_1": "string","parte_2": "string"},
    "instrucciones_finales_juez": "string"
  },
  "decision": {
    "criterios": ["string"],
    "matriz_veredicto": [{"criterio":"string","peso":0.2,"observaciones":"string"}],
    "resultados_alternativos": [{"escenario":"A","descripcion":"string"}]
  },
  "banco_preguntas": ["string"],
  "rubrica": [{"criterio":"Dominio normativo","niveles":{"excelente":"string","bueno":"string","basico":"string"},"puntaje_max":10}],
  "variantes": ["string"],
  "glosario": [{"termino":"string","definicion":"string"}]
}

Produce textos claros, consistentes y útiles para práctica académica. Concluye siempre con el bloque JSON válido.
"""


def build_user_prompt(request: SimulateRequest) -> str:
    """Create a descriptive prompt for the language model."""

    restricciones = "\n".join(f"- {item}" for item in (request.restricciones or []))
    if restricciones:
        restricciones_text = f"Restricciones adicionales:\n{restricciones}\n"
    else:
        restricciones_text = ""
    jurisdiccion = request.jurisdiccion or "Penal acusatorio hispano genérico"

    prompt = (
        "Genera una simulación de juicio completa considerando los siguientes datos:\n"
        f"Contexto (3-10 líneas):\n{request.contexto.strip()}\n\n"
        f"Jurisdicción: {jurisdiccion}\n"
        f"Materia: {request.materia}\n"
        f"Nivel: {request.nivel}\n"
        f"Objetivo didáctico: {request.objetivo_didactico}\n"
        f"Duración mínima estimada: {request.duracion_min} minutos\n"
        f"{restricciones_text}"
        "Recuerda mantener tono pedagógico, personajes ficticios y destacar objeciones frecuentes."
    )
    return prompt


async def call_openrouter(system_prompt: str, user_prompt: str) -> str:
    """Call OpenRouter chat completions API with retries."""

    settings = get_settings()
    payload: Dict[str, Any] = {
        "model": settings.openrouter_model,
        "fallbacks": settings.openrouter_fallbacks,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(60.0, read=60.0)
    attempts = 0
    last_exception: Exception | None = None

    async with httpx.AsyncClient(base_url=str(settings.openrouter_base_url)) as client:
        while attempts < 3:
            attempts += 1
            try:
                response = await client.post(
                    "", headers=headers, json=payload, timeout=timeout
                )
                if response.status_code == 429 and attempts < 3:
                    await asyncio.sleep(2 * attempts)
                    continue
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content
            except httpx.HTTPError as exc:  # includes timeout and status errors
                last_exception = exc
                LOGGER.error(
                    "Error calling OpenRouter (attempt %s): %s", attempts, exc
                )
                await asyncio.sleep(1.5 * attempts)

    raise RuntimeError("No se pudo obtener respuesta del modelo") from last_exception


__all__ = ["SYSTEM_PROMPT", "build_user_prompt", "call_openrouter"]
